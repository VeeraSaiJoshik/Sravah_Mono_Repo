import asyncio
import json
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
import os

api_key = os.getenv("OPENAI_API_KEY")

# Setup
client = OpenAI(api_key=api_key)


class BaseWrapper:
    def __init__(self, name):
        self.name = name
        self.history = []
        self.depth_counter = 0

    def ask(self, prompt):
        """Sync call to OpenAI API"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.history + [{"role": "system", "content": prompt}]
        )
        return resp.choices[0].message.content

    async def ask_async(self, prompt):
        """Async call to OpenAI API"""
        resp = await asyncio.to_thread(
            lambda: client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self.history + [{"role": "system", "content": prompt}]
            )
        )
        return resp.choices[0].message.content

#wrappers fromat above, prompts below

class Wrapper1(BaseWrapper):
    def run(self, user_input):
        self.history.append({"role": "user", "content": user_input})
        self.max_turns = 2
        while self.depth_counter < self.max_turns:
            question = self.ask(
                '''
                You are a conversational AI designed to help users describe their blockers.
                Ask a follow-up to gather more general info about hte blocker. Don't get too technical yet, and do not add any suggestions.

                Focus on gathering simple problem description information, how much time they have already spent trying to solve it,
                and what this blocker is preventing them from doing.

                Ultimately, your followups should lead to a clear general description of the blocker from a technology and business perspective.
                '''
                )
            
            print(f"Wrapper1: {question}")
            user_resp = input("User: ")
            self.history.append({"role": "assistant", "content": question})
            self.history.append({"role": "user", "content": user_resp})
            self.depth_counter += 1
        return self.history

class Wrapper2(BaseWrapper):
    def run(self):
        while self.depth_counter < 1:
            question = self.ask("Ask about what the user has alreay done to try and solve the blocker. Ask about where that has led them, and why they are still stuck.")
            print(f"Wrapper2: {question}")
            user_resp = input("User: ")
            self.history.append({"role": "assistant", "content": question})
            self.history.append({"role": "user", "content": user_resp})
            self.depth_counter += 1
        return self.history

class AsyncWrapper1(BaseWrapper):
    async def run(self, wrapper1_history, techstack_info, git_info, asana_board):
        self.history = wrapper1_history
        context = f'''
            Given the general blocker info, tech stack: {techstack_info}, git: {git_info}, asana: {asana_board} produce specific line_items to ask about.

            These line items could be two different things, listed as short sentences or phrases:

            1- missing topics/questions. These could be specific technical details (ex: user did not mention if they tried hitting db with postman, or they didn't talk about api credentials)
            2- asana. These are specific business visions about the overall project that the user has not given context to. What exact feature/subtask is this blocker realted to?

            '''
        result = await self.ask_async(context)
        return json.loads(result) if result.startswith("[") else [result]

class Wrapper3(BaseWrapper):
    def run(self, line_items):
        for item in line_items:
            answered = False
            while not answered:
                question = self.ask(f'''
                                    Ask the user about: {item}
                                    Make sure to ask in a way that is clear and concise, so the user can easily understand what you are asking.
                                ''')
                print(f"Wrapper3: {question}")
                user_resp = input("User: ")
                self.history.append({"role": "assistant", "content": question})
                self.history.append({"role": "user", "content": user_resp})
                answered = True
        return self.history

class Wrapper4(BaseWrapper):
    def run(self):
        confirmed = False
        while not confirmed:
            summary = self.ask("Summarize the user's blocker from the history. Then, ask the user to confirm that this analysis of the blocker is correct.")
            print(f"Summary: {summary}")
            user_resp = input("Is this correct? (yes/no) ")
            if user_resp.lower().startswith("y"):
                confirmed = True
        return self.history

class AsyncWrapper2(BaseWrapper):
    async def run(self, history):
        with open("match.json", "r") as f:
            matches = json.load(f)
        context = f"Given the blocker history: {history}, find the closest match from: {matches}"
        result = await self.ask_async(context)
        return result

class Wrapper5(BaseWrapper):
    def run(self, matched_solution, wrapper2_history):
        self.history = wrapper2_history
        prompt = f"Given the matched solution: {matched_solution}, suggest steps to solve the problem."
        solution = self.ask(prompt)
        print(f"Wrapper5 Suggestion: {solution}")

class Wrapper6(BaseWrapper):
    def run(self):
        with open("team.json", "r") as f:
            team_data = json.load(f)
        prompt = f"Given the blocker details, suggest the best team member to help from: {team_data}"
        person = self.ask(prompt)
        print(f"Wrapper6 Suggestion: {person}")


#callings
async def main():
    w1 = Wrapper1("Wrapper1", max_turns=3)
    w2 = Wrapper2("Wrapper2", max_turns=3)
    aw1 = AsyncWrapper1("AsyncWrapper1")
    w3 = Wrapper3("Wrapper3")
    w4 = Wrapper4("Wrapper4")
    aw2 = AsyncWrapper2("AsyncWrapper2")
    w5 = Wrapper5("Wrapper5")
    w6 = Wrapper6("Wrapper6")

    # Step 1: General Info
    blocker_desc = input("Describe your blocker: ")
    w1_history = w1.run(blocker_desc)

    # Step 2 + AsyncWrapper1
    w2_history = w2.run()
    aw1_task = asyncio.create_task(aw1.run(w1_history, "Python, React", "main branch commit hash"))
    line_items = await aw1_task

    # Step 3
    w3_history = w3.run(line_items)

    # Step 4 + AsyncWrapper2
    w4_history = w4.run()
    aw2_task = asyncio.create_task(aw2.run(w1_history + w2_history + w3_history))
    matched_solution = await aw2_task

    # Step 5
    w5.run(matched_solution, w2_history)

    # Step 6
    w6.run()

if __name__ == "__main__":
    asyncio.run(main())
