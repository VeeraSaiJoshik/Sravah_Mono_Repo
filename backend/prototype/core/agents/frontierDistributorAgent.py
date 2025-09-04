import json
from openai import OpenAI
from .base_agent import BaseAgent

class ClassificationAgent(BaseAgent):
    @property
    def purpose(self) -> str:
        return "Classifies standup updates into categories (Blockers, Yesterday, Today) and projects."

    async def run(self, raw_input: str, client: OpenAI) -> dict:
        try:
            system_prompt = """
            You are a parser and a responder that takes a developer's standup update and outputs
            a JSON structure grouping their statements by project and category, along with a response.

            Categories:
            - B  : Blockers (problems they couldn't solve)
            - YTD: What they did yesterday
            - TD : What they plan on doing today

            Each project is labeled P1, P2, ..., based on how many distinct projects appear.
            Some statements may belong to multiple categories or projects.

            Prioritize responding to a blocker. Only respond to one subnode. 
            This response should incite the user to provide more technical information.

            Output format (JSON only, no explanation):
            {
                "P1": {
                    "B": ["chunk1", "chunk2"],
                    "YTD": ["chunk3"],
                    "TD": ["chunk4"]
                },
                "P2": {
                    "B": [],
                    "YTD": [],
                    "TD": []
                },
                "response": "Your response to the user"
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
