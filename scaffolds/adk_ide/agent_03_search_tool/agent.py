"""
Agent for weather information.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

MODEL = "gemini-2.0-flash"

root_agent = Agent(
    name="search_agent_v3",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="Provides information about weather for specific cities.",
    instruction="""
    You are an expert **Weather Information Assistant**.

    When the user requests **weather information** for a **specific city**,
    you must use the **'google_search' tool** to find relevant information.

    If the tool returns an error or no events are found,
    **inform the user politely** that you could not find any
    events or that there might be an issue.

    If the tool is successful and returns events,
    **present the event suggestions clearly**,
    including the **event name, date, and a brief description** if available.
    """,
    # google_search is a pre-built tool
    # which allows the agent to perform Google searches.
    tools=[google_search],
)
