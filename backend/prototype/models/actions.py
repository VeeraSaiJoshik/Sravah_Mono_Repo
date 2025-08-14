from abc import ABC, abstractmethod
from openai import OpenAI
from backend.prototype.core.call_tree import tree
from backend.prototype.models.projects import Project

class Action(ABC) : 
    @abstractmethod
    async def run(self, raw_input: str, context_nodes: list[tree.Node], project: Project, client: OpenAI):
        pass