# main/orchestrator.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from core.agents.frontierDistributorAgent import FrontierDistributorAgent
from core.agents.blocker_agents.conversationAgents.triageWrapper1 import Wrapper1TriageAgent
from models.BlockerInternalDataTypes import TriageRecord, LineItemAnswer

QuestionTriage = "Before we get too deep in, could you quickly describe what the business implications of the blocker? Where is it currently reproducable/discoverd?"
response_flag = False
def main():
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("System: Welcome! Let’s begin your daily standup. Please tell me about yesterday, today, and blockers.")
    frontier_agent = FrontierDistributorAgent()

    while True:
        user_input = input("\nYou: ")
        result = frontier_agent.run(user_input, client=client)
        print(f"Assistant: {result.get('response', '[No response found]')}")
        print(f"System: {QuestionTriage}")
        user_input = input("\nYou: ")
        if response_flag == False:
            result = Wrapper1TriageAgent.run(user_input, client=client)
            response_text = result.get('response', '[No response found]')
            response_flag = result.get('done', False)
            print(response_text)
        #wrapper 2


if __name__ == "__main__":
    main()
