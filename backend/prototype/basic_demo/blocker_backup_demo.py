"""
BlockerSystem
|
├─ Wrapper1 (sync)  : Fast triage — REQUIRED fields (business impact + reproducibility + environment + short description)
|                     -> returns structured `triage_record`
|
├─ AsyncRetrieval (async, started immediately after wrapper 1 finishes, processes during wrapper 2) :
|                     -> fetch relevant external context in background:
|                        - matching Asana/Jira-like tickets (task management)
|                        - embeddings search over match.json (top-N similar past blockers)
|                        - keyword/term expansion using technical glossary
|
├─ AsyncWrapper1 (async, uses triage_record + retrieved context, same timeline as AsyncRetrieval) :
|                     -> *produces concrete* `line_items` (questions) with schema:
|                        {id, question, expected_type, why_it_matters, required, priority}
|
├─ Wrapper2 (sync)  : Ask what dev already tried (structured attempts)
|                     -> store as `attempts_record`
|
├─ Wrapper3 (sync)  : Ask the concrete `line_items` one-by-one (from AsyncWrapper1).
|                     -> mark each item answered
|
├─ Wrapper4 (sync)  : Summarize blocker concisely (2–3 sentence summary + key artifacts)
|                     -> Confirm loop (subwrapper4a summarize, subwrapper4b confirm)
|
├─ AsyncWrapper2 (async, runs right after wrapper 3 finishes, processing while wrapper 4 runs, input for wrapper 5) :
|                     -> take triage_record + attempts + answered_line_items and run final match
|                        (historical blockers embeddings + GPT re-ranker)
|
├─ Wrapper5 (sync)  : Suggest prioritized, runnable steps (short checklist + rationale)
|
└─ Wrapper6 (sync)  : Recommend team member(s) from team.json (best match + suggested ask text)

"""

from __future__ import annotations

import asyncio
import json
import math
import os
import random
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


try:
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


class Wrapper1_Triage(BaseWrapper):
    async def run(self):
        """Collect fast triage in a few turns and normalize to structure via LLM."""
        # Voice-first prompts
        q1 = "Quick headline and business impact?"
        q2 = "Where does it reproduce (env) and how consistently?"
        q3 = "Any brief notes I should know right away?"

        title_impact = (await io.ask(q1)).strip()
        env_repro = (await io.ask(q2)).strip()
        notes = (await io.ask(q3)).strip()

        sys_prompt = (
            "You are a strict triage normalizer. Given freeform answers, produce a JSON object with keys: "
            "title, impact, reproducibility, environment, notes. Use concise phrases."
        )
        content = f"Answers:\n1) {title_impact}\n2) {env_repro}\n3) {notes}"
        messages = [self.sys(sys_prompt), self.user(content)]
        result = await self.oai.chat_async(messages)

        try:
            data = json.loads(self._extract_json(result))
        except Exception:
            # best-effort fallback parse
            data = {
                "title": title_impact,
                "impact": "unspecified",
                "reproducibility": env_repro,
                "environment": env_repro,
                "notes": notes,
            }
        # Simple heuristics to split env/repro if user combined them
        env = data.get("environment") or "staging"
        rep = data.get("reproducibility") or ("100%" if "every" in env_repro.lower() else "intermittent")
        return TriageRecord(
            title=data.get("title", title_impact),
            impact=data.get("impact", "unspecified"),
            reproducibility=rep,
            environment=env,
            notes=data.get("notes", notes),
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        m = re.search(r"\{[\s\S]*\}", text)
        return m.group(0) if m else "{}"


class AsyncRetrieval:
    """Background retrieval over task mgmt, blockers, and glossary."""

    def __init__(self, store: DataStore):
        self.store = store
        self.tickets: List[Dict[str, Any]] = []
        self.blocker_candidates: List[Dict[str, Any]] = []
        self.glossary: Dict[str, str] = {}

    async def run(self, triage: TriageRecord) -> None:
        query = f"{triage.title} {triage.environment} {triage.notes} {triage.reproducibility}"
        # Parallelize simple retrievals
        t1 = asyncio.create_task(asyncio.to_thread(self.store.search_tickets, query, 5))
        t2 = asyncio.create_task(asyncio.to_thread(self.store.search_blockers, query, 8))
        t3 = asyncio.create_task(asyncio.to_thread(self.store.glossary_defs, ["sentiment-widget", "ml-service"]))
        self.tickets = await t1
        self.blocker_candidates = await t2
        self.glossary = await t3  # type: ignore


class AsyncWrapper1_GenerateLineItems(BaseWrapper):
    async def run(self, triage: TriageRecord, retrieval: AsyncRetrieval) -> List[LineItem]:
        context = {
            "triage_record": asdict(triage),
            "tickets": retrieval.tickets,
            "glossary": retrieval.glossary,
            "blocker_candidates_titles": [b["title"] for b in retrieval.blocker_candidates],
        }
        sys_prompt = (
            "You generate VOICE-FIRST follow-up questions as JSON array of objects with keys: "
            "id, question, expected_type, why_it_matters, required (bool), priority (high|medium|low). "
            "Questions must be answerable by speech (no links/uploads). Keep them short. "
            "Bias questions toward feature flags, ML service versions, cross-team dependencies, and environment specifics."
        )
        messages = [self.sys(sys_prompt), self.user(json.dumps(context))]
        out = await self.oai.chat_async(messages)
        try:
            arr = json.loads(self._extract_json_array(out))
        except Exception:
            # Fallback static minimal set
            arr = [
                {
                    "id": "li_voice_01",
                    "question": "Is the widget gated by any feature flags in staging?",
                    "expected_type": "yes_no_or_name",
                    "why_it_matters": "Flags commonly hide UI in non-prod",
                    "required": True,
                    "priority": "high",
                },
                {
                    "id": "li_voice_02",
                    "question": "Do you know if the ML model version in staging changed recently?",
                    "expected_type": "short_text",
                    "why_it_matters": "Stale model artifacts cause blanks",
                    "required": True,
                    "priority": "high",
                },
            ]
        return [LineItem(**li) for li in arr]

    @staticmethod
    def _extract_json_array(text: str) -> str:
        m = re.search(r"\[[\s\S]*\]", text)
        return m.group(0) if m else "[]"


class Wrapper2_Attempts(BaseWrapper):
    async def run(self, io: IOHandler) -> AttemptsRecord:
        q = (
            "What have you already tried? Name specifics like toggles, retries, rollbacks, config changes, quick fixes."
        )
        ans = (await io.ask(q)).strip()
        sys_prompt = (
            "Extract a bullet list of concrete attempts from the user's answer. Return JSON array of short strings."
        )
        messages = [self.sys(sys_prompt), self.user(ans)]
        out = await self.oai.chat_async(messages)
        try:
            items = json.loads(Wrapper1_Triage._extract_json(out))
            if isinstance(items, dict) and "items" in items:
                items = items["items"]
        except Exception:
            items = [ans]
        return AttemptsRecord(items=[i.strip() for i in items if i and isinstance(i, str)])


class Wrapper3_AskLineItems(BaseWrapper):
    async def run(self, io: IOHandler, items: List[LineItem]) -> List[LineItemAnswer]:
        answers: List[LineItemAnswer] = []
        for it in sorted(items, key=lambda x: {"high":0,"medium":1,"low":2}.get(x.priority, 1)):
            prompt = f"{it.question}"
            ans = (await io.ask(prompt)).strip()
            answers.append(LineItemAnswer(id=it.id, answer=ans))
        return answers


class Wrapper4_SummarizeConfirm(BaseWrapper):
    async def run(self, io: IOHandler, triage: TriageRecord, attempts: AttemptsRecord, li_answers: List[LineItemAnswer]) -> bool:
        context = {
            "triage": asdict(triage),
            "attempts": attempts.items,
            "answers": [asdict(a) for a in li_answers],
        }
        sys_prompt = (
            "Summarize the blocker in 2-3 sentences, crisp, including environment, impact, key hypothesis."
        )
        messages = [self.sys(sys_prompt), self.user(json.dumps(context))]
        summary = await self.oai.chat_async(messages)
        ok = await io.confirm(f"Here is the summary I will share: {summary}\nIs this correct?")
        return ok


class AsyncWrapper2_FinalMatch(BaseWrapper):
    def __init__(self, oai: OpenAIClient, store: DataStore, name: str = "AsyncWrapper2"):
        super().__init__(oai, name)
        self.store = store

    async def run(self, triage: TriageRecord, attempts: AttemptsRecord, li_answers: List[LineItemAnswer]) -> MatchResult:
        query = (
            f"{triage.title}. env={triage.environment}. repro={triage.reproducibility}. "
            f"attempts={'; '.join(attempts.items)}. answers={'; '.join(a.answer for a in li_answers)}"
        )
        cands = await asyncio.to_thread(self.store.search_blockers, query, 5)
        # Re-rank with GPT quickly using reasons
        sys_prompt = (
            "You are a matcher. Given a query and candidate blockers, choose the best single match and return a JSON with keys: "
            "best_id (or null) and reasons."
        )
        messages = [self.sys(sys_prompt), self.user(json.dumps({"query": query, "candidates": cands}))]
        out = await self.oai.chat_async(messages)
        try:
            data = json.loads(Wrapper1_Triage._extract_json(out))
            best_id = data.get("best_id")
            best = next((c for c in cands if c.get("id") == best_id), None)
        except Exception:
            best = cands[0] if cands else None
        return MatchResult(matched_blocker=best, candidates=cands)


class Wrapper5_SuggestSteps(BaseWrapper):
    async def run(
        self,
        io: IOHandler,
        triage: TriageRecord,
        attempts: AttemptsRecord,
        li_answers: List[LineItemAnswer],
        match: MatchResult,
    ) -> str:
        context = {
            "triage": asdict(triage),
            "attempts": attempts.items,
            "answers": [asdict(a) for a in li_answers],
            "match": match.matched_blocker,
        }
        sys_prompt = (
            "Produce a short, prioritized checklist of concrete next steps (voice-friendly). "
            "Focus on feature flags, verifying ML model version in staging, and looping in the ML owner if needed. "
            "Return 3-6 bullet points with rationale."
        )
        messages = [self.sys(sys_prompt), self.user(json.dumps(context))]
        steps = await self.oai.chat_async(messages)
        await io.say(f"Proposed next steps:\n{steps}")
        return steps


class Wrapper6_SuggestPerson(BaseWrapper):
    def __init__(self, oai: OpenAIClient, store: DataStore, name: str = "Wrapper6"):
        super().__init__(oai, name)
        self.store = store

    async def run(self, io: IOHandler, skills_needed: List[str]) -> Dict[str, Any]:
        candidates = self.store.find_team_candidates(skills_needed)
        top = candidates[0] if candidates else None
        if not top:
            await io.say("I couldn't find a teammate with the exact skills; I'll share the summary with the team channel.")
            return {}
        # Draft a ping message
        sys_prompt = (
            "Draft a concise Slack message to request help from the teammate, including the summary of the blocker and immediate asks."
        )
        msg = await self.oai.chat_async([self.sys(sys_prompt), self.user(json.dumps({"name": top["name"]}))])
        await io.say(
            f"Recommended contact: {top['name']} ({top['role']}) — Slack: {top['contact']['slack']}\nSuggested message:\n{msg}"
        )
        return top



class BlockerSession:
    def __init__(self, oai: OpenAIClient, store: DataStore, io: IOHandler):
        self.oai = oai
        self.store = store
        self.io = io
        # Wrappers
        self.w1 = Wrapper1_Triage(oai, "Wrapper1")
        self.retrieval = AsyncRetrieval(store)
        self.aw1 = AsyncWrapper1_GenerateLineItems(oai, "AsyncWrapper1")
        self.w2 = Wrapper2_Attempts(oai, "Wrapper2")
        self.w3 = Wrapper3_AskLineItems(oai, "Wrapper3")
        self.w4 = Wrapper4_SummarizeConfirm(oai, "Wrapper4")
        self.aw2 = AsyncWrapper2_FinalMatch(oai, store)
        self.w5 = Wrapper5_SuggestSteps(oai, "Wrapper5")
        self.w6 = Wrapper6_SuggestPerson(oai, store)

        # State
        self.triage: Optional[TriageRecord] = None
        self.attempts: Optional[AttemptsRecord] = None
        self.line_items: List[LineItem] = []
        self.li_answers: List[LineItemAnswer] = []
        self.match: Optional[MatchResult] = None

    async def run(self) -> None:
        # Wrapper1 (sync) — triage
        self.triage = await self.w1.run(self.io)

        # Start AsyncRetrieval immediately
        ret_task = asyncio.create_task(self.retrieval.run(self.triage))

        # Wrapper2 (sync) — attempts
        self.attempts = await self.w2.run(self.io)

        # Wait for retrieval to finish, then AsyncWrapper1 to generate line items
        await ret_task
        self.line_items = await self.aw1.run(self.triage, self.retrieval)

        # Wrapper3 (sync) — ask line items
        self.li_answers = await self.w3.run(self.io, self.line_items)

        # Wrapper4 (sync) — summarize + confirm
        ok = await self.w4.run(self.io, self.triage, self.attempts, self.li_answers)
        if not ok:
            await self.io.say("Okay, I’ll tweak the summary based on your feedback and proceed.")

        # AsyncWrapper2 — final match (can run while we summarize; here we start now for clarity)
        self.match = await self.aw2.run(self.triage, self.attempts, self.li_answers)

        # Wrapper5 — suggest steps
        _steps = await self.w5.run(self.io, self.triage, self.attempts, self.li_answers, self.match)

        # Wrapper6 — suggest person (we assume ML skills needed in this story)
        await self.w6.run(self.io, ["NLP", "Flask API", "Model Debugging"])  # skill hints


def main():
    import argparse

    parser = argparse.ArgumentParser(description="BlockerSystem – Agentic Standup Assistant")
    parser.add_argument("--demo", action="store_true", help="Run scripted demo (no interactive input)")
    args = parser.parse_args()

    if os.environ.get("OPENAI_API_KEY") is None:
        print("WARNING: OPENAI_API_KEY not set. The demo will use retries and fallback embeddings.")

    if args.demo:
        asyncio.run(run_demo())
    else:
        oai = OpenAIClient()
        store = DataStore(oai)
        io = ConsoleIO()
        session = BlockerSession(oai, store, io)
        asyncio.run(session.run())


if __name__ == "__main__":
    main()