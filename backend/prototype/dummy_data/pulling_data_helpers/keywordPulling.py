from pymongo import MongoClient

password = "4SnPc6Zp2dOyWToP"
username = "gvsharshith_db_user"
uri = f"mongodb+srv://{username}:{password}@development.edtqqxr.mongodb.net/?retryWrites=true&w=majority&appName=Development"

# connect to Mongo
client = MongoClient(uri)
db = client["BackendSymtheticData"]
collection = db["keywords"]

##THIS IS TO PULL ALL INFO
docs = collection.find({}) 
for doc in docs:
    print(doc)

##THIS IS TO PULL ONE KEY
doc = collection.find_one({}, {"ml-service": 1, "_id": 0})
print(doc)

#MULTIPLE FIELDS
doc = collection.find_one({}, {"sentiment-widget": 1, "emoji-edge-case": 1, "_id": 0})
print(doc)

#pulls all document objects, projects queried items
cursor = collection.find({}, {"ml-service": 1, "staging-environment": 1, "_id": 0})
for doc in cursor:
    print(doc)

#pulls only documents with queried items (filteringwh)
doc = collection.find_one({"sentiment-widget": {"$exists": True}})
print(doc)


