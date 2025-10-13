from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables
load_dotenv()

# MongoDB connection
password = "4SnPc6Zp2dOyWToP"
username = "gvsharshith_db_user"
uri = f"mongodb+srv://{username}:{password}@development.edtqqxr.mongodb.net/?retryWrites=true&w=majority&appName=Development"

# connect to Mongo
client = MongoClient(uri)
db = client["BackendSymtheticData"]
projects_collection = db["projects"]

# Load embedding model (downloads on first run, ~80MB)
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded!")

def generate_project_embedding(project: dict) -> list:
    # Combine name and description
    text = f"{project['name']} {project['description']}"
    embedding = model.encode(text)
    return embedding.tolist()


def add_embeddings_to_projects():
    # Get all projects
    projects = list(projects_collection.find({}))
    print(f"Found {len(projects)} projects")

    if not projects:
        print("No projects found in database!")
        return
    
    # Generate and update embeddings
    updated_count = 0
    for project in tqdm(projects, desc="Generating embeddings"):
        try:
            # Generate embedding
            embedding = generate_project_embedding(project)
            
            # Update document in MongoDB
            projects_collection.update_one(
                {"_id": project["_id"]},
                {"$set": {"embedding": embedding}}
            )
            
            updated_count += 1
            
        except Exception as e:
            print(f"\nError processing project {project.get('id', 'unknown')}: {e}")
            continue
    print(f"\n✅ Successfully added embeddings to {updated_count} projects!")


def create_vector_search_index():
    """
    Create Atlas Vector Search index.
    
    NOTE: This only works if you're using MongoDB Atlas (cloud).
    For local MongoDB, you'll need to use alternative similarity search.
    """
    print("\n" + "="*70)
    print("VECTOR SEARCH INDEX SETUP")
    print("="*70)
    print("""
If you're using MongoDB Atlas (cloud):
1. Go to Atlas UI → Database → Search
2. Create Search Index with this configuration:

{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 384,
      "similarity": "cosine"
    }
  ]
}

3. Name it: "project_vector_index"

If you're using local MongoDB:
- Vector search is NOT supported
- You'll need to use alternative similarity calculation
  (compute cosine similarity in Python)
    """)


if __name__ == "__main__":
    add_embeddings_to_projects()
    create_vector_search_index()
    
    print("\n✅ Done! Your projects now have embeddings.")