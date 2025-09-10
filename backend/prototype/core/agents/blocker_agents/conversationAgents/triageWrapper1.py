import json
from openai import OpenAI
from .baseAgent import BaseAgent


class Wrapper1TriageAgent(BaseAgent):
    @property
    def purpose(self) -> str:
        return "Checks if triage information is complete (title, impact, reproducibility)."

    def run(self, raw_input: str, client: OpenAI) -> dict:
        try:
            system_prompt = """
            You are a triage assistant. You will review the developer's response
            and decide whether all required fields are answered.

            Required fields:
            - Short description (title)
            - Business impact
            - Reproducibility

            Rules:
            1. If any field is missing, respond with a short follow-up asking only for that field.
               Example: "What about the business impact?" or "Can you clarify where it's reproducible?"
            2. If all fields are answered (even if user said 'I don’t know'), then respond:
               "Thanks. What have you tried so far to solve the issue?"
            3. Output JSON only, no extra commentary.

            Output format:
            {
                "response": "Your response to the user",
                "done": True if all fields found, otherwise False
                "collected": {
                    "title": "...",
                    "impact": "...",
                    "reproducibility": "..."
                }
            }
            """

            response = client.chat.completions.create(
                model="gpt-4.1",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_input}
                ],
                temperature=0
            )

            parsed = response.choices[0].message.content
            return json.loads(parsed)

        except Exception as e:
            return self.fallback(str(e))
