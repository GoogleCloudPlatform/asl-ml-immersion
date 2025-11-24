# pylint: skip-file
from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent-card.json"

remote_trending_agent = RemoteA2aAgent(
    name="find_trends",
    description="Searches for current trending topics on social media",
    agent_card=f"http://localhost:10020{AGENT_CARD_WELL_KNOWN_PATH}",
)

remote_analyzer_agent = RemoteA2aAgent(
    name="analyze_trends",
    description="Provides quantitative analysis of a specific trend",
    agent_card=f"http://localhost:10021{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Create the Host ADK Agent
host_agent = SequentialAgent(
    name="trend_analysis_host",
    sub_agents=[remote_trending_agent, remote_analyzer_agent],
)
root_agent = host_agent