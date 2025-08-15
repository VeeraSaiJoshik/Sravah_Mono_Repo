from beanie import Document

class User(Document):
    first_name: str
    last_name: str
    profile_pic: str
    email: str
    projects: list[str]

    class Settings:
        name = "Users"