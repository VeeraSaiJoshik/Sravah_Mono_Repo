from pymongo import MongoClient
from ..models.mongo_schema.Blockers_Schema import Blocker

# MongoDB credentials
username = "gvsharshith_db_user"
password = "4SnPc6Zp2dOyWToP"
uri = f"mongodb+srv://{username}:{password}@development.edtqqxr.mongodb.net/?retryWrites=true&w=majority&appName=Development"

client = MongoClient(uri)
db = client["BackendSymtheticData"]
collection = db["blockers"]

# Pull all blockers
all_docs = collection.find({})
all_blockers = [Blocker.from_mongo(doc) for doc in all_docs]

print("All Blockers:")
for b in all_blockers:
    print(b)
print("\n" + "-"*50 + "\n")

#Pull blockers resolved by a specific user
user = "Liam Patel"
docs_by_user = collection.find({"resolved_by": user})
blockers_by_user = [Blocker.from_mongo(doc) for doc in docs_by_user]

print(f"Blockers resolved by {user}:")
for b in blockers_by_user:
    print(b)
print("\n" + "-"*50 + "\n")

#Pull blockers with a specific tag
tag = "frontend"
docs_with_tag = collection.find({"tags": tag})
blockers_with_tag = [Blocker.from_mongo(doc) for doc in docs_with_tag]

print(f"Blockers with tag '{tag}':")
for b in blockers_with_tag:
    print(b)
