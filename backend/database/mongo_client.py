from pymongo import MongoClient
from config.settings import MONGO_URI, MONGO_DB_NAME

# Global client instance
_client = None
_db = None


def get_mongo_client():
    """Get or create MongoDB client."""
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
    return _client


def get_database():
    """Get database instance."""
    global _db
    if _db is None:
        client = get_mongo_client()
        _db = client[MONGO_DB_NAME]
    return _db


def get_collection(collection_name: str):
    """
    Get a specific collection by str input
    """
    db = get_database()
    return db[collection_name]


def close_connection():
    """Close MongoDB connection (call on shutdown)."""
    global _client
    if _client:
        _client.close()
        _client = None