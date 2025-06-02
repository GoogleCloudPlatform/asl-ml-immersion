# critique_agent.py
from google.adk.agents import Agent

MODEL = "gemini-1.0-pro"

critique_agent = Agent(
    name="critique_agent_v1",
    model=MODEL,
    description="Reviews a drafted essay from `session.state['drafted_essay']` and provides a critique, storing it in `session.state['essay_critique']`.",
    instruction="""You are the Critique Agent. Your role is to review the drafted essay provided in `session.state['drafted_essay']`.
Evaluate it for clarity, coherence, completeness, accuracy, and style.
Provide constructive feedback, suggest improvements, and identify any areas that might need further research or clarification.
The orchestrator will make your critique available in `session.state['essay_critique']`.""",
    tools=None
)
