# pylint: skip-file
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from .tools import get_pycon_events

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
    name="agent4_agent_tool",
    model="gemini-2.0-flash",  # Can be a string for Gemini or a LiteLlm object
    description="Provides information about PyCon events for specific cities.",
    instruction="""
    You are an expert **PyCon Events Suggestion Assistant**.
    
    When the user requests **event suggestions** for a **specific city**,
    you must use the **'get_pycon_events' tool first** to find relevant information.
    
    If the 'get_pycon_events' tool returns an error or no events are found, 
    then propose to use 'google_search_agent' to find relevant information.
    
    If the tool is successful and returns events, **present the event suggestions clearly**, 
    including the **event name, date, and a brief description** if available.
    """,
    tools=[get_pycon_events, AgentTool(agent=google_search_agent)],
)
