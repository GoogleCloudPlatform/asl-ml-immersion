# pylint: skip-file
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from python.agents.adk_agents.agent4_agent_tool.tools import get_pycon_events

MODEL = "gemini-2.0-flash"

# Create the Python Trending Topics ADK Agent
python_trending_agent = Agent(
    model="gemini-2.5-pro",
    name="python_trending_topics_agent",
    instruction="""
    You are a social media trends analyst related to python topics. 
    Your job is to search the web for current python trending topics,
    particularly from social platforms.

    When asked about trends:
    1. Search for "recent python trending topics" or similar queries
    2. Extract the top 3 trending topics
    3. Return them in a JSON format

    Focus on actual trends from the last 2 weeks.

    You MUST return your response in the following JSON format:
    {
        "trends": [
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            },
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            },
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            }
        ]
    }

    Only return the JSON object, no additional text.
    """,
    tools=[google_search],
)

# Create an agent with google search tool as a search specialist
google_search_agent = Agent(
    model='gemini-2.5-flash',
    name='google_search_agent',
    description='A search agent that uses google search to get latest information about upcoming PyCon events',
    instruction="""Use google search find information about upcoming PyCon events.
                If the tool is successful and returns events, **present the event suggestions clearly**, 
                including the **event name, date, and a brief description** if available.
                """,
    tools=[google_search],
)

root_agent = Agent(
    name="agent5_agent_tool",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="Provides information about PyCon events for specific cities and prepare a few trending python topics to submit",
    instruction="""
    You are an expert **PyCon Events Suggestion Assistant**.
    
    When the user requests **event suggestions** for a **specific city**,
    you must use the **'google_search_agent' tool first** to find relevant information.

    If the tool is successful and returns events, **present the event suggestions clearly**, 
    including the **event name, date, and a brief description** if available.
    
    Use 'python_trending_agent' subagent to propose several python-related topics for submission
    
    """,
    sub_agents=[python_trending_agent],
    tools=[AgentTool(agent=google_search_agent)],
)
