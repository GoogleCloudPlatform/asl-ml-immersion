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
import operator
import os
from typing import Annotated, List, TypedDict

import uvicorn
from dotenv import load_dotenv

# LangGraph & LangChain Imports
from langchain_core.messages import BaseMessage

# A2A Imports
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

# A2A Utils & Types
from a2a.utils import (
    new_agent_text_message,
    new_task,
    new_text_artifact,
)
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TransportProtocol,
)

# --- State Definition ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]


# --- Agent Logic Class ---
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        """Invoke the Hello World agent to generate a response."""
        return 'Hello, A2A World!'


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

        # 1. Update status to WORKING
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(
                    state=TaskState.working,
                    message=new_agent_text_message('Processing request...'),
                ),
                final=False,
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
        
        # 2. Update status to COMPLETED
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=context.task_id,
                context_id=context.context_id,
                status=TaskStatus(state=TaskState.completed),
                final=True,
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """Raise exception as cancel is not supported."""
        raise NotImplementedError('Cancel is not supported')


# --- Server Setup ---
hello_world_agent_card = AgentCard(
    name="Hello World A2A Agent",
    url="http://localhost:10023",
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


def create_agent_a2a_server(executor: AgentExecutor, agent_card: AgentCard) -> A2AStarletteApplication:
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    return A2AStarletteApplication(
        agent_card=agent_card, http_handler=handler
    )


async def run_agent_server(port: int) -> None:
    executor = HelloWorldAgentExecutor()
    app = create_agent_a2a_server(executor, hello_world_agent_card)

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
    print("Starting Hello World Agent on port 10023...")
    try:
        asyncio.run(run_agent_server(port=10023))
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
