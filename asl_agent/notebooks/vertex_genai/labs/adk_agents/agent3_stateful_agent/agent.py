# pylint: skip-file
from google.adk.agents import Agent

MODEL = "gemini-2.0-flash"

from .tools import (
    get_weather_stateful,
    say_goodbye,
    say_hello,
    set_user_preference,
)

greeting_agent = Agent(
    model=MODEL,
    name="greeting_agent",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. Do nothing else.",
    description="Handles simple greetings and hellos using the 'say_hello' tool.",
    tools=[say_hello],
)

farewell_agent = Agent(
    model=MODEL,
    name="farewell_agent",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",
    tools=[say_goodbye],
)

root_agent = Agent(
    name="weather_agent_v3_stateful",  # New version name
    model=MODEL,
    description="Main agent: Provides weather (state-aware unit), delegates greetings/farewells, saves report to state.",
    instruction="You are the main Weather Agent. Your job is to provide weather using 'get_weather_stateful'. "
    "If user want to change prefered temperature unit (Celsius/Fahrenheit), use 'set_user_preference' and and change 'user:temperature_unit' state."
    "The tool will format the temperature based on user preference stored in state. "
    "Delegate simple greetings to 'greeting_agent' and farewells to 'farewell_agent'. "
    "Handle only weather requests, greetings, and farewells.",
    tools=[
        get_weather_stateful,
        set_user_preference,
    ],  # Use the state-aware tool
    sub_agents=[greeting_agent, farewell_agent],  # Include sub-agents
    output_key="last_weather_report",  # <<< Auto-save agent's final weather response
)
