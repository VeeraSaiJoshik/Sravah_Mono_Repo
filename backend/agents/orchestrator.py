import anthropic
from typing import List, Dict, Tuple
from config.settings import ANTHROPIC_API_KEY, ORCHESTRATOR_MODEL, TEMPERATURE
from config.settings import CONFIDENCE_THRESHOLD_HIGH, CONFIDENCE_THRESHOLD_LOW
from utils.conversation_state import ConversationState
from agents.tools import TOOLS
from database.search import search_projects, format_search_results

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are a helpful PM automation assistant. Your primary job is to identify which project a developer is referring to when they mention their work or blockers.

Your capabilities:
- You have access to a search_projects tool that searches a database of projects
- You can ask clarifying questions to narrow down which project the user means
- You understand technical jargon and can extract key terms from casual conversation

Your workflow:
1. When a user mentions their work, extract key terms (e.g., "sentiment widget", "dashboard", "ML API")
2. Use search_projects tool with that context
3. Evaluate the search results:
   - If one project clearly matches (high similarity score, >0.80): Confirm with user
   - If multiple projects match closely (scores within 0.1 of each other): Ask user to choose
   - If no strong matches (all scores <0.50): Ask for more details
4. Return the project ID once confirmed

Important guidelines:
- Be conversational and friendly, not robotic
- When you call search_projects, you can include a brief message to the user like "Give me a second to double check with the database to make sure we are on the same page..." before the tool use
- Extract specific, meaningful things to query with (not generic words like "working" or "issue")
- Pay attention to technical terms, component names, and feature descriptions
- If the user mentions multiple things, focus on the most specific/unique terms

Remember: Your goal is to accurately identify which project ID the user is discussing."""


def execute_tool(tool_name: str, tool_input: Dict, state: ConversationState) -> str:
    if tool_name == "search_projects":
        query = tool_input["query"]
        print(f"\n🔍 [SEARCH] Searching for: '{query}'")
        
        # Call the search function
        results = search_projects(query)
        
        if not results:
            return "No matching projects found. The search returned no results."
        
        # Format results for the LLM
        formatted = format_search_results(results)
        
        print(f"   Found {len(results)} matches (top score: {results[0]['score']:.3f})")
        
        return formatted
    
    return f"Error: Unknown tool {tool_name}"


def run_orchestrator_turn(state: ConversationState, user_message: str) -> Tuple[str, bool]:
    """
    Args:
        state: Current conversation state
        user_message: User's message
        
    Returns:
        Tuple of (assistant's response, project_identified_flag)
    """
    state.add_message("user", user_message)
    state.turn_count += 1
    
    # Conversation loop (handles tool use)
    messages = state.messages.copy()
    project_identified = False
    
    while True:
        response = client.messages.create(
            model=ORCHESTRATOR_MODEL,
            max_tokens=2000,
            temperature=TEMPERATURE,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )
        
        # Check if Claude wants to use tools
        if response.stop_reason == "tool_use":
            # Extract any text content (the "brief message" before tool use)
            text_blocks = [block.text for block in response.content if block.type == "text"]
            if text_blocks:
                brief_message = " ".join(text_blocks)
                print(f"\n💭 [THINKING] {brief_message}")
            
            # Extract and execute tool calls
            tool_calls = [block for block in response.content if block.type == "tool_use"]
            
            tool_results = []
            for tool_call in tool_calls:
                result = execute_tool(tool_call.name, tool_call.input, state)
                
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_call.id,
                    "content": result
                })
            
            # Add assistant's response and tool results to conversation
            messages.append({
                "role": "assistant",
                "content": response.content
            })
            
            messages.append({
                "role": "user",
                "content": tool_results
            })
            
            # Continue loop to get final response
            continue
        
        else:
            # No more tool use - extract final response
            final_response = ""
            for block in response.content:
                if block.type == "text":
                    final_response += block.text
            
            # Check if response contains a project ID (simple heuristic)
            if "proj-" in final_response.lower() or "project id" in final_response.lower():
                project_identified = True
            
            # Save assistant's response
            state.add_message("assistant", final_response)
            
            return final_response, project_identified