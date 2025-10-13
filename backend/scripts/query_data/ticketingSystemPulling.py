from pymongo import MongoClient
from ..models.mongo_schema.ticketingSystem_Schema import Project, Ticket  # adjust import path for dev/prod

password = "4SnPc6Zp2dOyWToP"
username = "gvsharshith_db_user"
uri = f"mongodb+srv://{username}:{password}@development.edtqqxr.mongodb.net/?retryWrites=true&w=majority&appName=Development"

# connect to Mongo
client = MongoClient(uri)
db = client["BackendSymtheticData"]
collection_projects = db["projects"]
collection_tickets = db["tickets"]

def get_project_by_id_or_name(identifier: str) -> Project | None:
    """Try to find a project by name first, else by id."""
    query = {"name": identifier}
    doc = collection_projects.find_one(query)
    if not doc:
        query = {"id": identifier}
        doc = collection_projects.find_one(query)
    return Project.from_mongo(doc) if doc else None


def get_tickets_for_project(project_id: str) -> list[Ticket]:
    """Fetch all tickets linked to a project_id."""
    cursor = collection_tickets.find({"project_id": project_id})
    return [Ticket.from_mongo(doc) for doc in cursor]


# -------------------------------
# Example usage
# -------------------------------
identifier = "Customer Feedback Sentiment Dashboard"  # or "proj-122"

project = get_project_by_id_or_name(identifier)

if project:
    print(f"\nFound project: {project.id} - {project.name}")
    related_tickets = get_tickets_for_project(project.id)

    if related_tickets:
        print(f"\nTickets for project {project.id}:")
        for t in related_tickets:
            print(f"\nTicket: {t.id}")
            print(f"  Description: {t.description}")
            print(f"  Root Cause: {t.root_cause}")
            print(f"  Solution: {t.solution}")
    else:
        print("No tickets found for this project.")
else:
    print("Project not found.")


# # --- Query 1: by project id ---
# print("\nQuerying by project id...")
# doc = collection_projects.find_one({"id": "proj-112"})
# if doc:
#     project = Project.from_mongo(doc)
#     print(f"Found project by id: {project.id}")
# else:
#     print("No project found with that id.")


# # --- Query 2: by project name ---
# print("\nQuerying by project name...")
# doc = collection_projects.find_one({"name": "Customer Feedback Sentiment Dashboard"})
# if doc:
#     project = Project.from_mongo(doc)
#     print(f"Found project by name: {project.id}")
# else:
#     print("No project found with that name.")
