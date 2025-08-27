"""
BlockerSystem
|
├─ Wrapper1 (sync)  : Fast triage — REQUIRED fields (business impact + reproducibility + environment + short description)
|                     -> returns structured `triage_record`
|
├─ AsyncRetrieval (async, started immediately) :
|                     -> fetch relevant external context in background:
|                        - matching Asana/Jira-like tickets (task management)
|                        - embeddings search over match.json (top-N similar past blockers)
|                        - keyword/term expansion using technical glossary
|
├─ AsyncWrapper1 (async, uses triage_record + retrieved context) :
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
├─ AsyncWrapper2 (async) :
|                     -> take triage_record + attempts + answered_line_items and run final match
|                        (historical blockers embeddings + GPT re-ranker)
|
├─ Wrapper5 (sync)  : Suggest prioritized, runnable steps (short checklist + rationale)
|
└─ Wrapper6 (sync)  : Recommend team member(s) from team.json (best match + suggested ask text)

Notes
-----
- This file is self-contained and ships with small in-memory synthetic datasets.
  If files exist under ./data/*.json, they will be loaded instead, so you can
  drop your own datasets without changing code.
- I/O is abstracted via IOHandler so you can plug ConsoleIO (CLI), ScriptedIO
  (for tests/demos), or a VoiceIO adapter later.
- All OpenAI calls are wrapped in OpenAIClient with simple retry/backoff.
- Embedding-based similarity uses `text-embedding-3-small` by default.
- The wrappers store their own local histories; the Orchestrator maintains the
  global session state.

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


class OpenAIClient:
    """Thin wrapper around OpenAI API for chat + embeddings with retry/backoff."""

    def __init__(self, model: str = "gpt-4o-mini", embedding_model: str = "text-embedding-3-small"):
        if OpenAI is None:
            raise RuntimeError("openai package not available. Install `openai` >= 1.0.")
        self.client = OpenAI()
        self.model = model
        self.embedding_model = embedding_model

    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_retries: int = 4) -> str:
        delay = 0.8
        for attempt in range(max_retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(delay)
                delay *= 1.6
        return ""

    async def chat_async(self, messages: List[Dict[str, str]], temperature: float = 0.3) -> str:
        # Run sync method in a thread to avoid blocking
        return await asyncio.to_thread(self.chat, messages, temperature)

    def embed(self, text: str, max_retries: int = 3) -> List[float]:
        delay = 0.6
        for attempt in range(max_retries):
            try:
                e = self.client.embeddings.create(model=self.embedding_model, input=text)
                return e.data[0].embedding  # type: ignore
            except Exception:
                if attempt == max_retries - 1:
                    # Fallback: return a fake but deterministic vector for testing
                    random.seed(hash(text) % (2**32))
                    return [random.random() for _ in range(64)]
                time.sleep(delay)
                delay *= 1.6
        return [0.0] * 64



DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def _load_json_or_default(path: Path, default_obj: Any) -> Any:
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    return default_obj


# Defaults (small but realistic) — replace by dropping files into ./data
DEFAULT_TASK_MGMT = {
    "project": {
        "id": "proj-112",
        "name": "Customer Feedback Sentiment Dashboard",
        "description": "Web dashboard showing live sentiment scores powered by internal ML service.",
        "status": "In Progress",
        "milestones": [
            {"id": "ms-001", "name": "Frontend Integration", "due_date": "2025-08-15", "status": "In Progress"},
            {"id": "ms-002", "name": "ML Service Stability", "due_date": "2025-08-20", "status": "Pending"},
        ],
    },
    "tickets": [
        {
            "id": "UI-342",
            "title": "Sentiment scores not rendering in dashboard",
            "assigned_to": "Alice Johnson",
            "status": "Blocked",
            "dependencies": ["ML-212"],
            "description": "Frontend sentiment widget shows 'Loading...' indefinitely on staging.",
            "tags": ["frontend", "sentiment-widget", "staging"],
            "last_update": "2025-08-09",
        },
        {
            "id": "ML-212",
            "title": "Sentiment API returns null values for some requests",
            "assigned_to": "Liam Patel",
            "status": "In Progress",
            "dependencies": [],
            "description": "ML service intermittently returns null sentiment scores for certain review texts.",
            "tags": ["ml-service", "sentiment-api", "bug"],
            "last_update": "2025-08-08",
        },
    ],
}

DEFAULT_BLOCKERS = [
    {
        "id": "blk-104",
        "title": "Frontend widget blank when ML API returns empty payload",
        "core_issue": "Frontend not handling null/empty API responses.",
        "root_cause": "ML API failed for emoji-only reviews (edge case).",
        "solution": "Update ML to handle emojis; add frontend fallback for null values.",
        "tags": ["frontend", "ml-service", "api-null"],
        "resolved_by": "Liam Patel",
    },
    {
        "id": "blk-099",
        "title": "Dashboard stalls due to slow API responses",
        "core_issue": "API response time exceeded frontend timeout.",
        "root_cause": "Missing async handling and retry logic in React component.",
        "solution": "Add timeout extension + retry; improve API caching.",
        "tags": ["frontend", "performance", "ml-service"],
        "resolved_by": "Alice Johnson",
    },
]

DEFAULT_KEYWORDS = {
    "sentiment-widget": "React component showing customer sentiment pulled from internal ML service.",
    "ml-service": "Internal Flask API returning sentiment scores from v3 model.",
    "staging-environment": "Pre-production environment used for feature testing.",
    "emoji-edge-case": "Known limitation where emoji-only text yields null scores.",
}

DEFAULT_TEAM = [
    {
        "id": "u-001",
        "name": "Alice Johnson",
        "role": "Frontend Developer",
        "current_task": "Integrating sentiment-widget into dashboard",
        "skills": ["React", "TypeScript", "GraphQL"],
        "project_responsibilities": "Build UI components; integrate API; handle loading/error states.",
        "contact": {"slack": "@alice", "email": "alice@example.com"},
        "timezone": "America/Los_Angeles",
    },
    {
        "id": "u-002",
        "name": "Liam Patel",
        "role": "Machine Learning Engineer",
        "current_task": "Fixing sentiment API null score issue (ML-212)",
        "skills": ["Python", "NLP", "Flask API", "Model Debugging"],
        "project_responsibilities": "Maintain sentiment model; ensure API stability/perf.",
        "contact": {"slack": "@liam", "email": "liam@example.com"},
        "timezone": "America/Chicago",
    },
    {
        "id": "u-003",
        "name": "Maria Gomez",
        "role": "Project Manager",
        "current_task": "Tracking dashboard release milestones",
        "skills": ["Agile", "Jira", "Stakeholder Communication"],
        "project_responsibilities": "Coordinate across teams; manage deadlines.",
        "contact": {"slack": "@maria", "email": "maria@example.com"},
        "timezone": "America/New_York",
    },
]


class DataStore:
    """Loads and provides access to all data sources, with embedding cache."""

    def __init__(self, oai: OpenAIClient):
        self.oai = oai
        self.task_mgmt = _load_json_or_default(DATA_DIR / "task_mgmt.json", DEFAULT_TASK_MGMT)
        self.blockers = _load_json_or_default(DATA_DIR / "blockers.json", DEFAULT_BLOCKERS)
        self.keywords = _load_json_or_default(DATA_DIR / "keywords.json", DEFAULT_KEYWORDS)
        self.team = _load_json_or_default(DATA_DIR / "team.json", DEFAULT_TEAM)
        self._embedding_cache: Dict[str, List[float]] = {}
        self._build_embedding_index()

    def _build_embedding_index(self) -> None:
        for blk in self.blockers:
            text = f"{blk['title']}\n{blk['core_issue']}\n{blk['root_cause']}\n{blk['solution']}\n{' '.join(blk.get('tags', []))}"
            self._embedding_cache[blk["id"]] = self.oai.embed(text)

    def embed_text(self, text: str) -> List[float]:
        return self.oai.embed(text)

    @staticmethod
    def _cosine(a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(y * y for y in b))
        if na == 0 or nb == 0:
            return 0.0
        return dot / (na * nb)

    def search_blockers(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        qv = self.embed_text(query)
        scored: List[Tuple[float, Dict[str, Any]]] = []
        for blk in self.blockers:
            bv = self._embedding_cache.get(blk["id"], [])
            score = self._cosine(qv, bv)
            scored.append((score, blk))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [blk for score, blk in scored[:top_k]]

    def search_tickets(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # naive semantic-ish search: priority to tag/title matches, then embeddings over titles+descriptions
        tickets = self.task_mgmt.get("tickets", [])
        scored: List[Tuple[float, Dict[str, Any]]] = []
        qv = self.embed_text(query)
        for t in tickets:
            text = f"{t['title']}\n{t['description']}\n{' '.join(t.get('tags', []))}"
            tv = self.oai.embed(text)
            score = self._cosine(qv, tv)
            # small bonus if any tag word appears in query
            if any(tag in query.lower() for tag in t.get("tags", [])):
                score += 0.05
            scored.append((score, t))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:top_k]]

    def glossary_defs(self, terms: List[str]) -> Dict[str, str]:
        out = {}
        for term in terms:
            if term in self.keywords:
                out[term] = self.keywords[term]
        return out

    def find_team_candidates(self, skills_needed: List[str]) -> List[Dict[str, Any]]:
        scored: List[Tuple[int, Dict[str, Any]]] = []
        for person in self.team:
            skills = [s.lower() for s in person.get("skills", [])]
            overlap = len({s.lower() for s in skills_needed} & set(skills))
            scored.append((overlap, person))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [p for _, p in scored]



class IOHandler:
    async def ask(self, prompt: string) -> str:  # type: ignore[name-defined]
        raise NotImplementedError

    async def confirm(self, prompt: str) -> bool:
        raise NotImplementedError

    async def say(self, text: str) -> None:
        print(text)


class ConsoleIO(IOHandler):
    async def ask(self, prompt: str) -> str:
        print(prompt)
        return await asyncio.to_thread(sys.stdin.readline)

    async def confirm(self, prompt: str) -> bool:
        print(prompt + " (y/n)")
        ans = await asyncio.to_thread(sys.stdin.readline)
        return ans.strip().lower().startswith("y")


class ScriptedIO(IOHandler):
    """Feed predetermined answers for demo/testing."""

    def __init__(self, turns: List[str]):
        self.turns = turns
        self.idx = 0

    async def ask(self, prompt: str) -> str:
        # print prompts for visibility
        print(f"AI: {prompt}")
        if self.idx < len(self.turns):
            ans = self.turns[self.idx]
            self.idx += 1
        else:
            ans = ""
        print(f"User: {ans}")
        return ans

    async def confirm(self, prompt: str) -> bool:
        print(f"AI: {prompt} (y/n)")
        if self.idx < len(self.turns):
            ans = self.turns[self.idx]
            self.idx += 1
        else:
            ans = "y"
        print(f"User: {ans}")
        return ans.strip().lower().startswith("y")



@dataclass
class TriageRecord:
    title: str
    impact: str
    reproducibility: str
    environment: str
    notes: str


@dataclass
class AttemptsRecord:
    items: List[str] = field(default_factory=list)


@dataclass
class LineItem:
    id: str
    question: str
    expected_type: str = "short_text"
    why_it_matters: str = ""
    required: bool = True
    priority: str = "high"


@dataclass
class LineItemAnswer:
    id: str
    answer: str


@dataclass
class MatchResult:
    matched_blocker: Optional[Dict[str, Any]]
    candidates: List[Dict[str, Any]]



class BaseWrapper:
    def __init__(self, oai: OpenAIClient, name: str, max_turns: int = 2):
        self.oai = oai
        self.name = name
        self.history: List[Dict[str, str]] = []
        self.max_turns = max_turns
        self.depth = 0

    def sys(self, content: str) -> Dict[str, str]:
        return {"role": "system", "content": content}

    def asst(self, content: str) -> Dict[str, str]:
        return {"role": "assistant", "content": content}

    def user(self, content: str) -> Dict[str, str]:
        return {"role": "user", "content": content}


class Wrapper1_Triage(BaseWrapper):
    async def run(self, io: IOHandler) -> TriageRecord:
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


DEMO_TURNS = [
    # Wrapper1 triage (3 Qs)
    "Product page recommendation widget is blank; delays A/B launch, blocking.",
    "Staging only, reproduces every time.",
    "No errors visible to users, just an empty spot.",
    # Wrapper2 attempts
    "Checked network calls (no errors), cleared cache, redeployed widget, rolled back once.",
    # Wrapper3 line items (these will be generated; below are generic plausible answers)
    "There is a staging flag called rec_widget_staging; not sure if it is on.",
    "I think the ML model might be older in staging than prod.",
]


async def run_demo() -> None:
    oai = OpenAIClient()
    store = DataStore(oai)
    io = ScriptedIO(DEMO_TURNS)
    session = BlockerSession(oai, store, io)
    await session.run()


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
