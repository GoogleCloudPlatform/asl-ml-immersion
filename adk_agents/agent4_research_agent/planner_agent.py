# planner_agent.py
from google.adk.agents import Agent

MODEL = "gemini-1.0-pro"

planner_agent = Agent(
    name="planner_agent_v1",
    model=MODEL,
    description="Generates a structured plan or outline for an essay/report based on a given topic. Expects the topic in `session.state['current_topic']`.",
    instruction="""You are the Planner Agent. Your task is to create a detailed, structured outline for an essay or report on the topic provided.
The topic will be available in `session.state['current_topic']`.
Your output should be the plan itself, which the orchestrator will then place into `session.state['essay_plan']`.
Focus on creating a logical flow with main sections and potential sub-points. Do not write the essay itself.""",
    tools=None
)
