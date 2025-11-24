# pylint: skip-file
from google.adk.agents import Agent

MODEL = "gemini-2.0-flash"

from .tools import get_location
from .tools import get_weather

root_agent = Agent(
    name="weather_agent_v2",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="Provides weather information for specific cities based on your location",
    instruction="You are a helpful weather assistant. "
                "When the user asks for the weather in a specific city, "
                "use the 'get_weather' tool to find the information. "
                "If user doesnt specify a city, use the 'get_location' tool to find the information. "
                "If the tool returns an error, inform the user politely. "
                "If the tool is successful, present the weather report clearly.",
    tools=[get_location, get_weather],
)
