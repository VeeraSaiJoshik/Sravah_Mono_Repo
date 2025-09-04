import json
from openai import OpenAI
from baseAgent import BaseAgent
import call_tree.tree as tree
from models.projects import Project

class SummarizerAgent(BaseAgent):
    @property
    def purpose(self) -> str:
        return "Summarizes raw input and context into structured JSON for other agents."

    async def run(self, raw_input: str, context_nodes: list[tree.Node], project: Project, client: OpenAI) -> dict:
        try:
            # Gather context
            conversation_history = " ".join([n.profile.raw_convo_snippet for n in context_nodes])
            context_history = " ".join([" ".join(n.profile.context) for n in context_nodes])
            project_meta = project.model_dump()

            system_prompt = f"""
            You are a parser that extracts key details and outputs them in JSON.
            
            Context so far: {context_history}
            Conversation snippets: {conversation_history}
            Project metadata: {project_meta}

            Format your response as JSON only.
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
