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