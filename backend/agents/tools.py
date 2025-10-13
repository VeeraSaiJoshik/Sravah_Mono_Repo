# Tool schema for Anthropic API
TOOLS = [
    {
        "name": "search_projects",
        "description": "Search for projects by keywords, description, or topic. Returns the top matching projects with similarity scores. Use this when you need to identify which project the user is referring to.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query extracted from user's message (e.g., 'sentiment dashboard', 'widget blank', 'ML API')"
                }
            },
            "required": ["query"]
        }
    }
]