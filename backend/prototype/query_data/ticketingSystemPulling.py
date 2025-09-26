from pymongo import MongoClient
from ..models.mongo_schema.ticketingSystem_Schema import Project  # adjust import path

password = "4SnPc6Zp2dOyWToP"
username = "gvsharshith_db_user"
uri = f"mongodb+srv://{username}:{password}@development.edtqqxr.mongodb.net/?retryWrites=true&w=majority&appName=Development"

# connect to Mongo
client = MongoClient(uri)
db = client["BackendSymtheticData"]
collection = db["projects"]


# --- Query 1: by project id ---
print("\nQuerying by project id...")
doc = collection.find_one({"id": "proj-112"})
if doc:
    project = Project.from_mongo(doc)
    print(f"Found project by id: {project.id}")
else:
    print("No project found with that id.")


# --- Query 2: by project name ---
print("\nQuerying by project name...")
doc = collection.find_one({"name": "Customer Feedback Sentiment Dashboard"})
if doc:
    project = Project.from_mongo(doc)
    print(f"Found project by name: {project.id}")
else:
    print("No project found with that name.")
