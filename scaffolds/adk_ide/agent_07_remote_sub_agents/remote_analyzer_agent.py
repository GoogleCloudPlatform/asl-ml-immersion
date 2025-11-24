import asyncio
# Ignore all warnings
import warnings

import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
)

from google.adk.a2a.executor.a2a_agent_executor import (
    A2aAgentExecutor,
    A2aAgentExecutorConfig,
)

from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

warnings.filterwarnings("ignore")
import logging

logging.basicConfig(level=logging.ERROR)
from google.adk.tools import google_search

import logging

from dotenv import load_dotenv
from google.adk.agents import Agent

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

logger.info("Create Trend Analyzer Agent...")

# Create the Trend Analyzer ADK Agent
trend_analyzer_agent = Agent(
    model="gemini-2.5-pro",
    name="trend_analyzer_agent",
    instruction="""
    You are a data analyst specializing in trend analysis. When given a trending topic,
    perform deep research to find quantitative data and insights.

    For each trend you analyze:
    1. Search for statistics, numbers, and metrics related to the trend
    2. Look for:
       - Engagement metrics (views, shares, mentions)
       - Growth rates and timeline
       - Geographic distribution
       - Related hashtags or keywords
    3. Provide concrete numbers and data points

    Keep it somehow concise

    Always prioritize quantitative information over qualitative descriptions.
    """,
    tools=[google_search],
)

analyzer_agent_card = AgentCard(
    name="Trend Analyzer Agent",
    url="http://localhost:10021",
    description="Performs deep analysis of trends with quantitative data",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="analyze_trend",
            name="Analyze Trend",
            description="Provides quantitative analysis of a specific trend",
            tags=["analysis", "data", "metrics", "statistics"],
            examples=[
                "Analyze the RAG trend",
                "Get metrics for the LLM trend",
                "Provide data analysis for AI adoption trend",
            ],
        )
    ],
)

def create_agent_a2a_server(agent, agent_card):
    """Create an A2A server for any ADK agent.

    Args:
        agent: The ADK agent instance
        agent_card: The ADK agent card

    Returns:
        A2AStarletteApplication instance
    """
    runner = Runner(
        app_name=agent.name,
        agent=agent,
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
    )

    config = A2aAgentExecutorConfig()
    executor = A2aAgentExecutor(runner=runner, config=config)

    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    # Create A2A application
    return A2AStarletteApplication(
        agent_card=agent_card, http_handler=request_handler
    )

async def run_agent_server(agent, agent_card, port) -> None:
    """Run a single agent server."""
    app = create_agent_a2a_server(agent, agent_card)

    config = uvicorn.Config(
        app.build(),
        host="127.0.0.1",
        port=port,
        log_level="warning",
        loop="none",  # Important: let uvicorn use the current loop
    )

    server = uvicorn.Server(config)
    await server.serve()

def main():
    """
    The synchronous entry point that sets up the event loop
    and runs the async server.
    """

    # 2. Use asyncio.run() to execute the main coroutine
    print(f"Starting agent server")
    try:
        asyncio.run(
            run_agent_server(
                agent=trend_analyzer_agent,
                agent_card=analyzer_agent_card,
                port=10021
            )
        )
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()