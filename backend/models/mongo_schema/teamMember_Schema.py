from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional



@dataclass
class Contact:
    slack: str
    email: str

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Contact":
        return cls(
            slack=data.get("slack", ""),
            email=data.get("email", "")
        )
@dataclass
class TeamMember:
    id: str
    name: str
    role: str
    current_task: str
    skills: List[str] = field(default_factory=list)
    project_responsibilities: str = ""
    contact: Optional[Contact] = None
    timezone: str = ""

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "TeamMember":
        contact_data = data.get("contact", {})
        contact = Contact.from_mongo(contact_data) if contact_data else None

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            role=data.get("role", ""),
            current_task=data.get("current_task", ""),
            skills=data.get("skills", []),
            project_responsibilities=data.get("project_responsibilities", ""),
            contact=contact,
            timezone=data.get("timezone", "")
        )
