from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ConversationState:
    """Tracks the state of the PM automation conversation."""
    
    # Conversation history (for Claude API)
    messages: List[Dict] = field(default_factory=list)
    
    # Identified information
    identified_project_id: Optional[str] = None
    identified_project_name: Optional[str] = None
    confidence_score: Optional[float] = None
    
    # Metadata
    turn_count: int = 0
    
    def add_message(self, role: str, content):
        """
        Add a message to conversation history.
        
        Args:
            role: 'user' or 'assistant'
            content: Message content (can be string or list of content blocks)
        """
        self.messages.append({
            "role": role,
            "content": content
        })
    
    def set_identified_project(self, project_id: str, project_name: str, confidence: float):
        """Record identified project information."""
        self.identified_project_id = project_id
        self.identified_project_name = project_name
        self.confidence_score = confidence
    
    def get_summary(self) -> str:
        """Get a summary of the current state."""
        summary = [f"Turn: {self.turn_count}"]
        
        if self.identified_project_id:
            summary.append(f"Identified Project: {self.identified_project_name} ({self.identified_project_id})")
            summary.append(f"Confidence: {self.confidence_score:.2f}")
        else:
            summary.append("Project: Not yet identified")
        
        return " | ".join(summary)