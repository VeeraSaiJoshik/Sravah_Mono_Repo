from pymongo import MongoClient
from models.BlockerInternalDataStore import KeywordsData

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
    keywords_data = KeywordsData.from_mongo(doc)
    print(keywords_data)


#pulls all document objects, projects queried items
cursor = collection.find({}, {"ml-service": 1, "staging-environment": 1, "_id": 0})
print("\nprojecting queried, pulls all")
for doc in cursor:
    keywords_data = KeywordsData.from_mongo(doc)
    for k, v in keywords_data.keywords.items():
        print(f"{k}: {v}")


#pulls only documents with queried items (filteringwh)
print("\nfiltering")
doc = collection.find_one({"sentiment-widget": {"$exists": True}})
if doc:
    keywords_data = KeywordsData.from_mongo(doc)
    print(keywords_data.keywords.get("sentiment-widget"))

