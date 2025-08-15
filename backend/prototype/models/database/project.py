from beanie import Document, Link
from typing import List
from pydantic import BaseModel
from enum import Enum
from prototype.models.database.user import User

class TechType(str, Enum):
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DATABASE = "Database"
    DEVOPS = "DevOps"
    MOBILE = "Mobile"
    CLOUD = "Cloud"
    AI_ML = "AI/ML"
    SECURITY = "Security"
    OTHER = "Other"

class TechStack(BaseModel):
    technology_name: str
    technology_category: TechType
    usage_summary: str


class ServiceType(str, Enum):
    AUTHENTICATION = "Authentication"
    EXTERNAL_API = "External API"
    PAYMENT = "Payment"
    POS_SYSTEM = "POS System"
    ANALYTICS = "Analytics"
    COMMUNICATION = "Communication"
    STORAGE = "Storage"
    MONITORING = "Monitoring"
    OTHER = "Other"

class Services(BaseModel):
    service_name: str
    type: ServiceType
    provider: str
    integration_summary: str
    documentation_link: str
    
class BusinessTerms(BaseModel):
    term: str
    definition: str

class ProjectDetails(Document):
    project_name: str
    project_summary_tech: str
    project_summary_business: str
    tech_stack: list[TechStack]   
    services: list[Services]
    business_logic: list[BusinessTerms]

    class Settings: 
        name="Projects"
        allow_enums=True

class UserRoles(BaseModel):
    project: Link[ProjectDetails]
    members: List[Link[User]]