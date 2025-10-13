import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

# Agent Configuration
MAX_NEGOTIATION_ROUNDS = 20  # Prevent infinite loops
TEMPERATURE = 0.7

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "pm_automation")

# Check if using MongoDB Atlas (supports $vectorSearch) or local
IS_ATLAS = "mongodb.net" in MONGO_URI or "mongodb+srv" in MONGO_URI

# Model Configuration
ORCHESTRATOR_MODEL = "claude-sonnet-4-20250514"
TEMPERATURE = 0.7

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSIONS = 384

# Search Configuration
SEARCH_LIMIT = 5  # Top N results to return
CONFIDENCE_THRESHOLD_HIGH = 0.80  # Auto-confirm project
CONFIDENCE_THRESHOLD_LOW = 0.50   # Ask for more context

# Project Paths
BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"