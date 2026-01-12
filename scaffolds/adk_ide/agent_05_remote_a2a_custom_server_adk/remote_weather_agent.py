# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import logging
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
from dotenv import load_dotenv
from google.adk.a2a.executor.a2a_agent_executor import (
    A2aAgentExecutor,
    A2aAgentExecutorConfig,
)
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

MODEL = "gemini-2.0-flash"

from .tools import get_weather

logger.info("Create Weather Agent ...")

# Create the Weather Agent ADK Agent
weather_agent = Agent(
    name="weather_agent_v2",  # Give it a new version name
    model=MODEL,
    description="Handles weather information requests using the 'get_weather' tool.",
    instruction="You are the Weather Agent. Your primary responsibility is to provide weather information. "
    "Use the 'get_weather' tool for weather requests (e.g., 'weather in London'). "
    "Do not perform any other actions.",
    tools=[get_weather],
)

weather_agent_card = AgentCard(
    name="Weather Agent",
    url="http://localhost:10021",
    description="Provides weather information",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="get_weather",
            name="Get Weather",
            description="Provides actual weather information",
            tags=["weather","information"],
            examples=[
                "Get weather in London",
                "What is the weather in New York?",
                "Provide weather information for Paris",
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
    print("Starting agent server")
    try:
        asyncio.run(
            run_agent_server(
                agent=weather_agent,
                agent_card=weather_agent_card,
                port=10021,
            )
        )
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
    except RuntimeError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
