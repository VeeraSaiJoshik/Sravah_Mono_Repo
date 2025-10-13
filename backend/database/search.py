from typing import List, Dict
from database.mongo_client import get_collection
from database.embeddings_CosineSimilarity import generate_embedding, cosine_similarity
from config.settings import SEARCH_LIMIT, IS_ATLAS


def search_projects_atlas(query: str, limit: int = SEARCH_LIMIT) -> List[Dict]:
    #search through atlast cloud
    # Generate query embedding
    query_embedding = generate_embedding(query)
    
    projects_collection = get_collection("projects")
    
    # Use Atlas $vectorSearch
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 3,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "id": 1,
                "name": 1,
                "description": 1,
                "status": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    results = list(projects_collection.aggregate(pipeline))
    return results


def search_projects_local(query: str, limit: int = SEARCH_LIMIT) -> List[Dict]:
    #manual cosine search
    # Generate query embedding
    query_embedding = generate_embedding(query)
    
    projects_collection = get_collection("projects")
    
    # Get all projects with embeddings
    projects = list(projects_collection.find(
        {"embedding": {"$exists": True}},
        {"_id": 0, "id": 1, "name": 1, "description": 1, "status": 1, "embedding": 1}
    ))
    
    if not projects:
        print("No projects found with embeddings.")
        return []
    
    # Calculate similarity for each project
    for project in projects:
        similarity = cosine_similarity(query_embedding, project["embedding"])
        project["score"] = similarity
        # Remove embedding from result (don't need to show it)
        del project["embedding"]
    
    # Sort by similarity (highest first)
    projects.sort(key=lambda x: x["score"], reverse=True)
    
    # Return top N
    return projects[:limit]


def search_projects(query: str, limit: int = SEARCH_LIMIT) -> List[Dict]:
    #calls above functions based on what DB is available
    if IS_ATLAS:
        try:
            return search_projects_atlas(query, limit)
        except Exception as e:
            print(f"⚠️  Atlas search failed: {e}")
            print("Falling back to local search...")
            return search_projects_local(query, limit)
    else:
        return search_projects_local(query, limit)


def format_search_results(results: List[Dict]) -> str:
    """
    Format search results for display to LLM.
    
    Args:
        results: List of project dictionaries with scores
        
    Returns:
        Formatted string representation
    """
    if not results:
        return "No matching projects found."
    
    formatted = []
    for i, project in enumerate(results, 1):
        formatted.append(
            f"{i}. {project['name']} (ID: {project['id']})\n"
            f"   Description: {project['description']}\n"
            f"   Status: {project.get('status', 'Unknown')}\n"
            f"   Similarity Score: {project['score']:.3f}"
        )
    
    return "\n\n".join(formatted)