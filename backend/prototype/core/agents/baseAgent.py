from abc import ABC, abstractmethod
import json

class BaseAgent(ABC):
    @property
    @abstractmethod
    def purpose(self) -> str:
        """Short description of what this agent is meant to do."""
        pass

    @abstractmethod
    def run(self, raw_input: str) -> dict:
        """Run the agent on input and return structured output."""
        pass

    def fallback(self, error_message: str = "An error occurred") -> dict:
        """Common fallback JSON for all agents."""
        return {"error": error_message, "output": None}
