from pymongo import MongoClient
from ..models.mongo_schema.teamMember_Schema import TeamMember

password = "4SnPc6Zp2dOyWToP"
username = "gvsharshith_db_user"
uri = f"mongodb+srv://{username}:{password}@development.edtqqxr.mongodb.net/?retryWrites=true&w=majority&appName=Development"

# connect to Mongo
client = MongoClient(uri)
db = client["BackendSymtheticData"]
team_members = db["teamMembers"]


def get_team_members_by_name(name: str) -> list[TeamMember]:
    cursor = team_members.find({"name": name})
    return [TeamMember.from_mongo(doc) for doc in cursor]


def get_team_members_by_role(role: str) -> list[TeamMember]:
    cursor = team_members.find({"role": role})
    return [TeamMember.from_mongo(doc) for doc in cursor]



print("\nQuerying by name...")
members = get_team_members_by_name("Alice Johnson")
for m in members:
    print(f"{m.name} ({m.role}) - Responsibilities: {m.project_responsibilities}")


print("\nQuerying by role...")
members = get_team_members_by_role("Frontend Developer")
for m in members:
    print(f"{m.name} ({m.role}) - Responsibilities: {m.project_responsibilities}")
