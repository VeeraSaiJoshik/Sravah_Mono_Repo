# main/orchestrator.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from core.agents.frontierDistributorAgent import FrontierDistributorAgent

def main():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("System: Welcome! Let’s begin your daily standup. Please tell me about yesterday, today, and blockers.")
    frontier_agent = FrontierDistributorAgent()

    while True:
        user_input = input("\nYou: ")
        result = frontier_agent.run(user_input, client = client)
        print(f"Assistant: {result.get('response', '[No response found]')}")


if __name__ == "__main__":
    main()
