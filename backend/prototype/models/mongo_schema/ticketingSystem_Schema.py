from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Milestone:
    id: str
    name: str
    due_date: str  #todo: do we want to keep this as str, or have some logic for coerceing to datetime?
    status: str

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Milestone":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            due_date=data.get("due_date", ""),
            status=data.get("status", ""),
        )


@dataclass
class Project:
    id: str
    name: str
    description: str
    status: str
    milestones: List[Milestone] = field(default_factory=list)

    @classmethod
    def from_mongo(cls, data: Dict[str, Any]) -> "Project":
        milestones = [
            Milestone.from_mongo(m) for m in data.get("milestones", [])
        ]
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            status=data.get("status", ""),
            milestones=milestones,
        )
