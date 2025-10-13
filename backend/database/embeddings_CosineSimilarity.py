from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL
import numpy as np
from typing import List

# Global model instance (lazy loaded)
_model = None


def get_embedding_model():
    #Get or load embedding model (lazy loading).
    global _model
    if _model is None:
        print("Loading embedding model (this may take a moment on first run)...")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        print("Model loaded!")
    return _model


def generate_embedding(text: str) -> List[float]:
    #Generate embedding vector for a text string.
    model = get_embedding_model()
    embedding = model.encode(text)
    return embedding.tolist()


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    #similarity score between vec1 and vec2, vec1 is query, vec2 could be list of projects?
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    
    # Cosine similarity formula
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))