from datetime import datetime
from pydantic import BaseModel

class Targets(BaseModel) : 
    name: str
    description: str
    technology: list[str]
    deadline: datetime

class Lingo(BaseModel) : 
    name: str
    definition: str

    def __str__(self) : 
        return f"{self.name} : {self.definition}"

class Project(BaseModel) : 
    about: str
    project_name: str
    major_targets: list[Targets]
    project_summary_tech: str
    project_summary_business: str
    primary_kpi_goal: str

    tech_stack: list[str]
    lingo: list[Lingo]