from openai import OpenAI
from backend.prototype.core.call_tree import tree
from backend.prototype.models.actions import Action
from backend.prototype.models.projects import Project

class Distributor(Action):
    async def run(self, raw_input: str, context_nodes: list[tree.Node], project: Project, client: OpenAI):
        """
            Takes a raw user response from a developer's standup and
            classifies it into a structure: {project: {category: [chunks]}}
            Categories = "B" (Blockers), "YTD" (Yesterday), "TD" (Today)
        """
        system_prompt = """
        You are a parser and a responder that takes a developer's standup update and outputs
        a JSON structure grouping their statements by project and category, along with a response.

        Categories:
        - B  : Blockers (problems they couldn't solve)
        - YTD: What they did yesterday
        - TD : What they plan on doing today

        Each project is labeled P1, P2, ..., based on how many distinct projects appear.
        Some statements may belong to multiple categories or projects.

        prioritize responding to a blocker. Only respond to one subnode. this response should incite the user to provide more technical information.

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
            }
            "response": "Your response to the user"
        }
        """

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_response}
            ],
            temperature=0
        )

        return response.choices[0].message.content
