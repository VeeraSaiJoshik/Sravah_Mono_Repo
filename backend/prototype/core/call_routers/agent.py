from backend.prototype.models.actions import Action
import call_tree.tree as tree
from models.projects import Project
from openai import OpenAI
from abc import ABC, abstractmethod
import json

class Agent(Action): 
    @abstractmethod
    def action(self, params):
        pass

    @abstractmethod
    @property
    def purpose(self) -> str:
        return ""

    @abstractmethod
    @property
    def input_schema(self) -> dict:
        return {}
    
    async def run(self, raw_input: str, context_nodes: list[tree.Node], project: Project, client: OpenAI):
        input_scehma = dict(self.input_schema)
        input_scehma["error_response"] = "a question that the audio agent should ask the user for additional information to perform the task of the agent which currently is not available. Make sure this response is worded in a way that it aligns with the rest of the conversation"

        conversation_history = " ".join([node.profile.raw_convo_snippet for node in context_nodes])
        context_history = " ".join([node.profile.context for node in context_nodes])
        project_meta = project.model_dump()

        system_prompt = f"""
            You are a raw text parser that parses a raw response and creates a json body for a data retrieval agent. 
            a JSON structure grouping their statements by project and category, along with a response.

            Here is the relevant conversational context up until this point from the conversation : {context_history}
            Here is the relevant content from external sources that have been pulled throughout this conversation : {conversation_history}
            Here is relevant information about the project relating to which this conversation is : {project_meta}

            Here is the information regarding the purpose of the agent you are summarizing information for : {self.purpose}
            
            Please process the user input and extract the useful information from the user response and the provided context to provide useful input to the agent

            

            Output format (JSON only, no explanation):
            {input_scehma}
        """

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_input}
            ],
            temperature=0
        )
        agent_input = response.choices[0].message.content

        return await self.action(json.loads(agent_input))


