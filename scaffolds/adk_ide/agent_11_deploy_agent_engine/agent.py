# pylint: skip-file
from google.adk.agents import Agent

MODEL = "gemini-2.0-flash"

from .tools import get_pycon_events

root_agent = Agent(
    name="pycon_agent_v1",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="Provides information about PyCon events for specific cities.",
    instruction="""
    You are an expert **PyCon Events Suggestion Assistant**.
    
    When the user requests **event suggestions** for a **specific city and date range**,
    you must use the **'get_pycon_events' tool** to find relevant information.
    
    If the tool returns an error or no events are found, **inform the user politely** that you could not find any events or that there might be an issue.
    
    If the tool is successful and returns events, **present the event suggestions clearly**, including the **event name, date, and a brief description** if available.
    """,
    tools=[get_pycon_events],  # Pass the function directly
)
