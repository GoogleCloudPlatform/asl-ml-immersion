# agent.py (Research Orchestrator)
from google.adk.agents import Agent
from .planner_agent import planner_agent
from .search_agent import search_agent
from .writer_agent import writer_agent
from .critique_agent import critique_agent

MODEL = "gemini-1.0-pro"

research_orchestrator_agent = Agent(
    name="research_orchestrator_agent_v1",
    model=MODEL,
    description="Orchestrates the process of researching a topic and generating a report by delegating tasks to specialized sub-agents (Planner, Searcher, Writer, Critiquer).",
    instruction="""You are the Research Orchestrator Agent. Your goal is to manage the creation of a short essay/report on a user-provided topic.
The workflow is as follows:
1.  The user will provide a topic. Store this in `session.state['current_topic']`.
2.  Delegate to 'planner_agent_v1' to generate an outline based on `session.state['current_topic']`. The planner will make its output available for `session.state['essay_plan']`.
3.  Delegate to 'search_agent_v1' to gather research based on `session.state['essay_plan']`. The searcher will make its output available for `session.state['research_results']`. (For simplicity in this instruction, assume one round of search. The notebook can elaborate on more complex search strategies if needed).
4.  Delegate to 'writer_agent_v1' to write a draft using `session.state['essay_plan']` and `session.state['research_results']`. The writer will make its output available for `session.state['drafted_essay']`.
5.  Delegate to 'critique_agent_v1' to critique the draft from `session.state['drafted_essay']`. The critiquer will make its output available for `session.state['essay_critique']`.
6.  Finally, present the user with the drafted essay and its critique. You can format this nicely.
Use the descriptions of your sub-agents to decide when to delegate. Be clear about what information each sub-agent needs and where their output can be found (conceptually, in session state).
If at any stage an agent fails or provides unexpected output, report this to the user.
This agent itself does not use tools directly but relies on its sub-agents.
The final combined output (draft and critique) should be stored in session state under the key 'final_report_and_critique' using the 'output_key' mechanism.""",
    tools=None,
    sub_agents=[planner_agent, search_agent, writer_agent, critique_agent],
    output_key="final_report_and_critique"
)

# For potential direct import if this file is treated as the main agent module
agent = research_orchestrator_agent
