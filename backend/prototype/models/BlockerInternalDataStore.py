from dataclasses import dataclass, field
from typing import List, Dict, Optional

# KeyWords.json
@dataclass
class KeywordEntry:
    keyword: str
    description: str


@dataclass
class KeywordsData:
    keywords: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_mongo(cls, doc: dict) -> "KeywordsData":
        if "_id" in doc:
            doc.pop("_id")
        return cls(keywords=doc)

# #Blockers.json
# @dataclass
# class Blocker:
#     id: str
#     title: str
#     core_issue: str
#     root_cause: str
#     solution: str
#     tags: List[str] = field(default_factory=list)
#     resolved_by: str = ""





# #TaskManagement.json
# @dataclass
# class Milestone:
#     id: str
#     name: str
#     due_date: str
#     status: str


# @dataclass
# class Project:
#     id: str
#     name: str
#     description: str
#     status: str
#     milestones: List[Milestone] = field(default_factory=list)


# @dataclass
# class Ticket:
#     id: str
#     title: str
#     assigned_to: str
#     project_id: str
#     description: str = ""
#     asignee: str
#     asignee_email: str = ""
#     status: str
#     created_at: str
#     updated_at: str
#     tags: List[str] = field(default_factory=list)
#     dependencies: List[str] = field(default_factory=list)
#     root_cause: str
#     solution: str = ""
#     milestone: str
#     priority: str = ""
#     comments_count: int = 0

# @dataclass
# class TaskManagement:
#     project: Project
#     tickets: List[Ticket] = field(default_factory=list)


# #Team.json
# @dataclass
# class Contact:
#     slack: str
#     email: str


# @dataclass
# class TeamMember:
#     id: str
#     name: str
#     role: str
#     current_task: str
#     skills: List[str] = field(default_factory=list)
#     project_responsibilities: str = ""
#     contact: Contact = None
#     timezone: str = ""


# @dataclass
# class Team:
#     members: List[TeamMember] = field(default_factory=list)
