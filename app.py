import os
from flask import Flask, request, jsonify
from googleapiclient.discovery import build
from crewai import Agent, Task, Process, Crew
from langchain.tools import Tool

app = Flask(__name__)

open_ai_key = "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"
api_gemini = "AIzaSyBRz438Gg-Mnb4s1mfRYEJOB86ec3is2o4"  # Replace with your Google API key
cse_api_key = "AIzaSyDKlUeIBPsqm_rgDF743yKUmH95FY2xdxw"  # Your CSE API Key
cse_id = "521cbec02241348fc"  # Your CSE ID

class GoogleSerperAPIWrapper:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id

    def run(self, query):
        service = build("customsearch", "v1", developerKey=self.api_key)
        res = service.cse().list(q=query, cx=self.cse_id).execute()
        return [item['link'] for item in res.get('items', [])]

search = GoogleSerperAPIWrapper(cse_api_key, cse_id)
search_tool = Tool(
    name="Scrape google searches",
    func=search.run,
    description="Useful for when you need to ask the agent to search the internet",
)

class CustomAgent:
    def __init__(self, openai_api_key):
        self.ai = ChatOpenAI(openai_api_key=openai_api_key)  # Adjust this according to your actual import and API setup

explorer = Agent(
    role="Senior Researcher",
    goal="Find and explore the most exciting AI projects and companies on the internet.",
    backstory="Expert strategist in AI, tech and machine learning, adept at finding exciting projects.",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool],
)
writer = Agent(
    role="Senior Technical Writer",
    goal="Write engaging blog posts about the latest AI projects.",
    backstory="Skilled in crafting compelling narratives about technological innovations.",
    verbose=True,
    allow_delegation=True,
)
critic = Agent(
    role="Expert Writing Critic",
    goal="Provide feedback and ensure blog posts are engaging and understandable.",
    backstory="Expert at providing insightful critiques to enhance the clarity and appeal of texts.",
    verbose=True,
    allow_delegation=True,
)

crew = Crew(
    agents=[explorer, writer, critic],
    tasks=[],
    verbose=2,
    process=Process.sequential,
)

@app.route('/process', methods=['POST'])
def process():
    task_description = request.json.get('task_description', '')
    task = Task(
        description=task_description,
        agent=explorer,
        expected_output="A detailed report on AI projects with names and descriptions.",
    )
    crew.tasks = [task]
    result = crew.kickoff()
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
