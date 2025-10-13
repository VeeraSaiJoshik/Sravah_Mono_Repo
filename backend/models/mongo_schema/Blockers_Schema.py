# Blockers.json (Mongo-friendly schema)
from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Blocker:
    id: str
    title: str
    core_issue: str
    root_cause: str
    solution: str
    tags: List[str] = field(default_factory=list)
    resolved_by: str = ""

    @classmethod
    def from_mongo(cls, doc: Dict) -> "Blocker":
        doc_copy = doc.copy()
        doc_copy.pop("_id", None)  # remove MongoDB _id
        return cls(**doc_copy)
