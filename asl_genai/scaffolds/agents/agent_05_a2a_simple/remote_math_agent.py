from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

MODEL = "gemini-2.0-flash"

def add_two_numbers(a: float, b: float) -> float:
    """Adds numbers (a + b)"""
    print(f"--- Tool: add_two_numbers called with a: {a} b: {b} ---")
    return a + b 

def subtract_two_numbers(a: float, b: float) -> float:
    """Subtracts numbers (a - b)"""
    print(f"--- Tool: subtract_two_numbers called with a: {a} b: {b} ---")
    return a - b

weather_agent = Agent(
    name="math_agent",
    model=MODEL,
    description="Handles mathematical operations like addition and subtraction.",
    instruction="You are the Math Agent. you handle mathematical operations like addition and subtraction.",
    tools=[add_two_numbers, subtract_two_numbers],
)
root_agent = weather_agent

a2a_app = to_a2a(root_agent, port=10020)