from dataclasses import dataclass, field
from typing import List, Dict, Optional


#Blockers.json
@dataclass
class Blocker:
    id: str
    title: str
    core_issue: str
    root_cause: str
    solution: str
    tags: List[str] = field(default_factory=list)
    resolved_by: str = ""


# KeyWords.json
@dataclass
class KeywordEntry:
    keyword: str
    description: str


@dataclass
class KeywordsData:
    keywords: Dict[str, str] = field(default_factory=dict)


#TaskManagement.json
@dataclass
class Milestone:
    id: str
    name: str
    due_date: str
    status: str


@dataclass
class Project:
    id: str
    name: str
    description: str
    status: str
    milestones: List[Milestone] = field(default_factory=list)


@dataclass
class Ticket:
    id: str
    title: str
    assigned_to: str
    status: str
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    tags: List[str] = field(default_factory=list)
    last_update: str = ""


@dataclass
class TaskManagement:
    project: Project
    tickets: List[Ticket] = field(default_factory=list)


#Team.json
@dataclass
class Contact:
    slack: str
    email: str


@dataclass
class TeamMember:
    id: str
    name: str
    role: str
    current_task: str
    skills: List[str] = field(default_factory=list)
    project_responsibilities: str = ""
    contact: Contact = None
    timezone: str = ""


@dataclass
class Team:
    members: List[TeamMember] = field(default_factory=list)
