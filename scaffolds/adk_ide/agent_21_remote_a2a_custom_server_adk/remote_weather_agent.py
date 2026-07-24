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
import os
import uvicorn

# Starlette & A2A SDK v1.0.0+ imports
from starlette.applications import Starlette
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

# Import AgentInterface alongside other types
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    AgentInterface,
)
from dotenv import load_dotenv

# ADK imports
from google.adk.a2a.executor.a2a_agent_executor import (
    A2aAgentExecutor,
    A2aAgentExecutorConfig,
)
from google.adk.agents import Agent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

# Load environment variables from .env file
try:    
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    print(f"Loading .env from {env_file}")
    load_dotenv(dotenv_path=env_file)
except Exception as e:
    print(f"Error loading .env file: {e}")

MODEL = "gemini-2.5-flash"
logger.info("Create Weather Agent ...")

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"--- Tool: get_weather called for city: {city} ---")  # Log tool execution
    city_normalized = city.lower().replace(" ", "")  # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C.",
        },
        "london": {
            "status": "success",
            "report": "It's cloudy in London with a temperature of 15°C.",
        },
        "tokyo": {
            "status": "success",
            "report": "Tokyo is experiencing light rain and a temperature of 18°C.",
        },
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"Sorry, I don't have weather information for '{city}'.",
        }

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

# A2A v1.0.0+ Compliant AgentCard instantiation
weather_agent_card = AgentCard(
    name="Weather Agent",
    description="Provides weather information",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    supported_interfaces=[
        AgentInterface(
            url="http://localhost:10021",
            protocol_binding="JSONRPC",
        )
    ],
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
        Starlette application instance
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
    
    # Request handler configuration
    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    # Starlette integration
    routes = [
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(request_handler, '/'),  # <-- Resolved missing 'rpc_url' parameter
    ]
    return Starlette(routes=routes)

async def run_agent_server(agent, agent_card, port) -> None:
    """Run a single agent server."""
    app = create_agent_a2a_server(agent, agent_card)
    
    # Bind server to the Starlette app
    config = uvicorn.Config(
        app,
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
    print("Starting agent server...")
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
