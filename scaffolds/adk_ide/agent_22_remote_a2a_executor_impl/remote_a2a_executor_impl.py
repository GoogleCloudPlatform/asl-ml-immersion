
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
import operator
import re
import uuid
from typing import Annotated, Any, Dict, List, Optional, TypedDict

import uvicorn
from dotenv import load_dotenv

# LangGraph & LangChain Imports
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import END, StateGraph

# A2A Imports
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    Part,
    TextPart,
    TransportProtocol,
)
from a2a.utils import completed_task, new_artifact

load_dotenv()

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather_agent_langgraph")


# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# --- Agent Logic Class ---
import operator
from typing import Annotated, TypedDict, List, Union, Dict, Any

# from langchain_core.tools import tool
# from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
# from langchain_google_vertexai import ChatVertexAI
# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import ToolNode, tools_condition

# --- 1. Define State & Tools (Module Level) ---
# class AgentState(TypedDict):
#     messages: Annotated[List[BaseMessage], operator.add]

class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        """Invoke the Hello World agent to generate a response."""
        return 'Hello, World!'


class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self) -> None:
        self.agent = HelloWorldAgent()


async def execute(
    self,
    context: RequestContext,
    event_queue: EventQueue,
) -> None:
    """Execute the agent process and enqueue the final response."""
    task = context.current_task or new_task(context.message)
    await event_queue.enqueue_event(task)

    await event_queue.enqueue_event(
        TaskStatusUpdateEvent(
            task_id=context.task_id,
            context_id=context.context_id,
            status=TaskStatus(
                state=TaskState.TASK_STATE_WORKING,
                message=new_agent_text_message('Processing request...'),
            ),
        )
    )

    result = await self.agent.invoke()

    await event_queue.enqueue_event(
        TaskArtifactUpdateEvent(
            task_id=context.task_id,
            context_id=context.context_id,
            artifact=new_text_artifact(name='result', text=result),
        )
    )
    await event_queue.enqueue_event(
        TaskStatusUpdateEvent(
            task_id=context.task_id,
            context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
        )
    )


# --- Server Setup ---

weather_agent_card = AgentCard(
    name="Hello World A2A Agent",
    url="http://localhost:10025",
    description="Simple A2A server implementation",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="say_hello",
            name="Say Hello",
            description="Returns a greeting",
            tags=["hello", "info"],
            examples=["Say hello"],
        )
    ],
)

def create_agent_a2a_server(executor, agent_card):
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    return A2AStarletteApplication(
        agent_card=agent_card, http_handler=handler
    )

async def run_agent_server(port) -> None:
    agent_logic = HelloWorldAgent()
    executor = HelloWorldAgentExecutor(agent=agent_logic)
    app = create_agent_a2a_server(executor, weather_agent_card)

    config = uvicorn.Config(
        app.build(),
        host="127.0.0.1",
        port=port,
        log_level="info",
        loop="none",
    )

    server = uvicorn.Server(config)
    await server.serve()

def main():
    print("Starting Say Hello Agent...")
    try:
        asyncio.run(run_agent_server(port=10022))
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Load environment variables from .env file
    try:    
        env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        print(f"Loading .env from {env_file}")
        load_dotenv(dotenv_path=env_file)
    except Exception as e:
        print(f"Error loading .env file: {e}")  
    main()