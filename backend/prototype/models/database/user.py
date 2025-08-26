from typing import List
from beanie import Document, Link
from pydantic import BaseModel

from backend.prototype.models.database.project import ProjectDetails, Services, TechStack

class User(Document):
    first_name: str
    last_name: str
    profile_pic: str
    email: str
    phone_number: str
    projects: list[str]
    role: str

    class Settings:
        name = "User"

class UserRole(BaseModel):
    project: Link[ProjectDetails]
    user: Link[User]
    tech_stacks: List[TechStack]
    services: List[Services]
    Suboordinates: List[Link[User]]
    Bosses: List[Link[User]]
    internal: bool
    action_items: List[str]

    class Settings: 
        name = "UserRole"