# This is an intermediate schema, where agents use raw datasource and create weighted lists, summaries, etc. for other
# 'main agents', that expect certain input. raw data -> intermediate agents -> expected data format (here) -> main agent -> user


from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


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
    matched_blocker: Optional[Dict[str, float]] = None
    candidates: List[Dict[str, float]] = field(default_factory=list)
