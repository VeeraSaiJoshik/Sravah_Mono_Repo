from typing import Dict, Any, List
from core.base_agent import BaseAgent
from models.datatypes import TriageRecord
from openai import OpenAI
import json


class Wrapper1TriageAgent(BaseAgent):

    @property
    def purpose(self) -> str:
        return "Conversational triage: collect short description, business impact, and reproducibility."


    REQUIRED_FIELDS = ["title", "impact", "reproducibility", "summary"]
    OPTIONAL_FIELDS = ["notes"]

    def __init__(self, client, model: str = "gpt-4o-mini"):
        super().__init__(client=client, model=model)
        self.system_prompt = (
            "You are a triage assistant. Your job is to quickly collect the "
            "required blocker information from the user.\n\n"
            "Fields to collect:\n"
            "- Short description (title)\n"
            "- Business impact\n"
            "- Reproducibility\n"
            "- Environment\n"
            "- Notes (optional)\n\n"
            "Rules:\n"
            "1. If a field is missing, ask a short, natural follow-up.\n"
            "2. If the user says 'I don’t know' or similar, treat that as answered with value 'unknown'.\n"
            "3. Do not keep asking once a field is answered, even if 'unknown'.\n"
            "4. Stop asking once all required fields are filled.\n"
            "5. Output your work as JSON at the end."
        )

    def run_loop(self, conversation_history: List[Dict[str, str]]) -> TriageRecord:
        """
        Loop until all required fields are collected.
        conversation_history is a list of {"role": "user"/"assistant", "content": "..."}
        """
        collected: Dict[str, Any] = {field: "" for field in self.REQUIRED_FIELDS + self.OPTIONAL_FIELDS}

        while True:
            # Ask the LLM what’s still missing
            user_prompt = (
                f"Conversation so far:\n{conversation_history}\n\n"
                f"Collected so far: {json.dumps(collected, indent=2)}\n\n"
                "Decide:\n"
                "1. Which fields are still missing?\n"
                "2. If missing, propose the next follow-up question.\n"
                "3. If all fields are complete, return FINAL JSON in this format:\n"
                "{'title': ..., 'impact': ..., 'reproducibility': ..., 'environment': ..., 'notes': ...}"
            )

            raw_response = self.run(
                system_prompt=self.system_prompt,
                user_prompt=user_prompt
            )

            try:
                data = json.loads(raw_response)
            except Exception:
                # If it’s not clean JSON, just keep it in notes
                data = {"notes": raw_response}

            # Merge new data
            for field in collected.keys():
                if field in data and data[field]:
                    collected[field] = data[field]

            # Check if all required fields are filled
            if all(collected[f] for f in self.REQUIRED_FIELDS):
                break

            # Otherwise: ask follow-up
            missing = [f for f in self.REQUIRED_FIELDS if not collected[f]]
            next_field = missing[0]
            followup_question = f"Can you tell me about {next_field}?"
            conversation_history.append({"role": "assistant", "content": followup_question})

            # In real orchestration, we’d now wait for user reply
            break  # <--- orchestration will re-call this method after user replies

        return TriageRecord(
            title=collected["title"],
            impact=collected["impact"],
            reproducibility=collected["reproducibility"],
            environment=collected["environment"],
            notes=collected.get("notes", "")
        )
