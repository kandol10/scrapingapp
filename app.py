import os
from flask import Flask, request, jsonify  # Import Flask and jsonify
from googleapiclient.discovery import build
from crewai import Agent, Task, Process, Crew
from langchain.tools import Tool

# Initialize Flask app
app = Flask(__name__)

# Assuming ChatOpenAI is a part of a library that needs to be imported
# from your_library import ChatOpenAI  # Ensure this is correct

# API keys setup
GOOGLE_API_KEY = "AIzaSyDKlUeIBPsqm_rgDF743yKUmH95FY2xdxw"
#OPENAI_API_KEY = "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"
CSE_ID = "521cbec02241348fc"
os.environ['OPENAI_API_KEY'] = 'sk-proj-4iQgSQqsMjy3YuQAqY6gT3BlbkFJQnoB3BbzQOfSmkhe7zJv'



class GoogleSerperAPIWrapper:
    def __init__(self, api_key, cse_id):
        self.api_key = api_key
        self.cse_id = cse_id

    def run(self, query):
        service = build("customsearch", "v1", developerKey=self.api_key)
        res = service.cse().list(q=query, cx=self.cse_id).execute()
        return [item['link'] for item in res.get('items', [])]

# Initialize the search tool with the API key and CSE ID
search = GoogleSerperAPIWrapper(GOOGLE_API_KEY, CSE_ID)
search_tool = Tool(
    name="Scrape google searches",
    func=search.run,
    description="Useful for when you need to ask the agent to search the internet",
)

# Assuming ChatOpenAI requires an API key
class CustomAgent:
    def __init__(self, openai_api_key):
        self.ai = ChatOpenAI(openai_api_key=openai_api_key)  # Ensure this is the correct usage

# Define agents
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

# Define tasks
task_report = Task(
    description="Summarize the latest AI projects found on the internet into a detailed report.",
    agent=explorer,
    expected_output="A detailed report on AI projects with names and descriptions.",
)

task_blog = Task(
    description="Write a blog article summarizing the latest AI projects.",
    agent=writer,
    expected_output="A blog article with compelling descriptions of AI projects.",
)

task_critique = Task(
    description="Ensure the blog article is engaging and properly formatted.",
    agent=critic,
    expected_output="Feedback ensuring the article is engaging and well-formatted.",
)

# Instantiate crew of agents
crew = Crew(
    agents=[explorer, writer, critic],
    tasks=[task_report, task_blog, task_critique],
    verbose=2,
    process=Process.sequential,
)

# Define the Flask route for processing tasks
@app.route('/process', methods=['POST'])
def process():
    # You may want to secure this endpoint or validate input
    task_description = request.json.get('task_description', '')
    task = Task(
        description=task_description,
        agent=explorer,
        expected_output="A detailed report on AI projects with names and descriptions.",
    )
    crew.tasks = [task]
    result = crew.kickoff()
    return jsonify(result)  # Return the result as JSON

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
