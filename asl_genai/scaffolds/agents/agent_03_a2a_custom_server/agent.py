from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from .tools import say_goodbye, say_hello

MODEL = "gemini-2.0-flash"

greeting_agent = Agent(
    model=MODEL,
    name="greeting_agent",
    instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting to the user. "
    "Use the 'say_hello' tool to generate the greeting. "
    "If the user provides their name, make sure to pass it to the tool. "
    "Do not engage in any other conversation or tasks.",
    description="Handles simple greetings and hellos using the 'say_hello' tool.",  # Crucial for delegation
    tools=[say_hello],
)

farewell_agent = Agent(
    model=MODEL,
    name="farewell_agent",
    instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message. "
    "Use the 'say_goodbye' tool when the user indicates they are leaving or ending the conversation "
    "(e.g., using words like 'bye', 'goodbye', 'thanks bye', 'see you'). "
    "Do not perform any other actions.",
    description="Handles simple farewells and goodbyes using the 'say_goodbye' tool.",  # Crucial for delegation
    tools=[say_goodbye],
)

# Using RemoteA2aAgent to communicate with Weather Agent
weather_agent = RemoteA2aAgent(
    name="weather_agent_v2",
    description="Handles weather information requests using the 'get_weather' tool.",
    agent_card=f"http://localhost:10021/.well-known/agent-card.json",
)

root_agent = Agent(
    name="coordination_agent",
    model=MODEL,
    description="You are the Weather Agent. Your primary responsibility is to provide weather information",
    instruction="You are the main Weather Agent coordinating a team. Your primary responsibility is to coordinate sub-agents."
    "You have specialized sub-agents: "
    "1. 'greeting_agent': Handles simple greetings like 'Hi', 'Hello'. Delegate to it for these. "
    "2. 'farewell_agent': Handles simple farewells like 'Bye', 'See you'. Delegate to it for these. "
    "3. 'weather_agent_v2': Handles weather information requests like 'weather in London'. Delegate to it for these. "
    "Analyze the user's query. If it's a greeting, delegate to 'greeting_agent'. If it's a farewell, delegate to 'farewell_agent'. "
    "If it's a weather request, delegate to 'weather_agent_v2'. "
    "For anything else, respond appropriately or state you cannot handle it.",
    sub_agents=[greeting_agent, farewell_agent, weather_agent],
)