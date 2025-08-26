from beanie import Document, Link
from prototype.models.database.user import User

class Organization(Document):
    organization_name: str
    admin: Link[User]
    profile_picture: str
    primary_color: str
    
    class Settings : 
        name = "Organization"