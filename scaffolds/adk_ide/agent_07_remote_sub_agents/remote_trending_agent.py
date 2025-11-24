# from a2a.client import ClientConfig, ClientFactory, create_text_message_object
# from a2a.server.apps import A2AStarletteApplication
# from a2a.server.request_handlers import DefaultRequestHandler
# from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)
# from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH
# from dotenv import load_dotenv
# from google.adk.a2a.executor.a2a_agent_executor import (
#     A2aAgentExecutor,
#     A2aAgentExecutorConfig,
# )
# from google.adk.agents import Agent, SequentialAgent
# from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
# from google.adk.artifacts import InMemoryArtifactService
# from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
# from google.adk.runners import Runner
# from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

import logging
import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
#from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.agents import Agent

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

logger.info("Creating ADK Trending Topics Agent")

root_agent = Agent(
    model="gemini-2.5-flash",
    name="trending_topics_agent",
    instruction="""
    You are a social media trends analyst related to python topics. 
    Your job is to search the web for current python trending topics,
    particularly from social platforms.

    When asked about trends:
    1. Search for "recent python trending topics" or similar queries
    2. Extract the top 3 trending topics
    3. Return them in a JSON format

    Focus on actual trends from the last 2 weeks.

    You MUST return your response in the following JSON format:
    {
        "trends": [
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            },
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            },
            {
                "topic": "Topic name",
                "description": "Brief description (1-2 sentences)",
                "reason": "Why it's trending"
            }
        ]
    }

    Only return the JSON object, no additional text.
    """,
    tools=[google_search],
)

# Make the agent A2A-compatible
a2a_app = to_a2a(root_agent, port=10020)