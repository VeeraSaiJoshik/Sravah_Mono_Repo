from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional

@dataclass
class TriageRecord:
    title: str
    impact: str
    reproducibility: str
    environment: str
    notes: str

@dataclass
class AttemptsRecord:
    items: List[str] = field(default_factory=list)

@dataclass
class LineItem:
    id: str
    question: str
    expected_type: str = "short_text"
    why_it_matters: str = ""
    required: bool = True
    priority: str = "high"

@dataclass
class LineItemAnswer:
    id: str
    answer: str

@dataclass
class MatchResult:
    matched_blocker: Optional[Dict[str, Any]]
    candidates: List[Dict[str, Any]]
