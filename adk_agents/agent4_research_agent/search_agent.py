# search_agent.py
from google.adk.agents import Agent
from .tools import google_search

MODEL = "gemini-1.0-pro"

search_agent = Agent(
    name="search_agent_v1",
    model=MODEL,
    description="Uses the 'google_search' tool to find information based on queries or topics provided in `session.state['search_queries']` (a list of strings) or `session.state['essay_plan']`. Stores results in `session.state['research_results']`.",
    instruction="""You are the Search Agent. Your role is to use the 'google_search' tool to find relevant information.
You will receive search queries (as a list of strings) in `session.state['search_queries']` or an essay plan in `session.state['essay_plan']` from which you should derive search queries.
For each query, execute the search and compile the results.
The orchestrator expects the compiled research findings to be made available for `session.state['research_results']`.
Present the findings clearly, perhaps as a list of snippets.""",
    tools=[google_search]
)
