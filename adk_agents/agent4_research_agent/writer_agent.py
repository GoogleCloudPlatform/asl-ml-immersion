# writer_agent.py
from google.adk.agents import Agent

MODEL = "gemini-1.0-pro"

writer_agent = Agent(
    name="writer_agent_v1",
    model=MODEL,
    description="Writes a draft of an essay/report based on a plan from `session.state['essay_plan']` and research from `session.state['research_results']`. Stores the draft in `session.state['drafted_essay']`.",
    instruction="""You are the Writer Agent. Your task is to write a coherent and well-structured first draft of an essay or report.
You will be provided with an essay plan (in `session.state['essay_plan']`) and research findings (in `session.state['research_results']`).
Use this information to write the draft.
The orchestrator will make your draft available in `session.state['drafted_essay']`.
Adhere to the plan and incorporate the research naturally.""",
    tools=None
)
