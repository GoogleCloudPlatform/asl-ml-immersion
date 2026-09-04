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
import os
import uuid
import inspect
from typing import List, Dict, Any
import uvicorn
from dotenv import load_dotenv

from starlette.applications import Starlette

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes

from a2a.types import (
    AgentCapabilities, AgentCard, AgentSkill, TaskState, 
    Message, Part, Role, Task, TaskStatus
)

# Load AgentInterface if supported in this environment (introduced in A2A SDK 1.0+)
try:
    from a2a.types import AgentInterface
except ImportError:
    AgentInterface = None

# ==============================================================================
# 1. DYNAMIC SDK ENUMS & FIELD CASING RESOLVERS
# ==============================================================================

ROLE_AGENT = getattr(Role, "ROLE_AGENT", getattr(Role, "agent", None))
TS_SUBMITTED = getattr(TaskState, "TASK_STATE_SUBMITTED", getattr(TaskState, "submitted", None))
TS_WORKING = getattr(TaskState, "TASK_STATE_WORKING", getattr(TaskState, "working", None))


def get_valid_fields(model_cls) -> set:
    """Extracts valid field names across Protobuf, Pydantic, or annotated types."""
    if hasattr(model_cls, "DESCRIPTOR"):
        return {f.name for f in model_cls.DESCRIPTOR.fields}
    for attr in ("model_fields", "__fields__", "__annotations__"):
        if hasattr(model_cls, attr):
            return set(getattr(model_cls, attr).keys())
    return set()


def create_model(model_cls, **kwargs) -> Any:
    """Universal model factory that filters and normalizes field mappings dynamically."""
    valid = get_valid_fields(model_cls)
    resolved = {}
    for k, v in kwargs.items():
        if k in valid:
            resolved[k] = v
        else:
            # Fallback to camelCase matching if the snake_case key is not found
            camel = "".join(w.capitalize() if i > 0 else w for i, w in enumerate(k.split("_")))
            if camel in valid:
                resolved[camel] = v
    return model_cls(**resolved)


# ==============================================================================
# 2. ADAPTIVE MODEL HELPERS
# ==============================================================================

def make_text_part(text: str) -> Part:
    """Generates a text Part object supporting both V1 flat layout and V0.3 nested specs."""
    try:
        return Part(text=text)
    except Exception:
        from a2a.types import TextPart
        return Part(root=TextPart(text=text))


def local_new_task(request: Message) -> Task:
    """Creates a Task instance dynamically mapping snake_case/camelCase variables."""
    t_id = getattr(request, "task_id", getattr(request, "taskId", None)) or str(uuid.uuid4())
    c_id = getattr(request, "context_id", getattr(request, "contextId", None)) or str(uuid.uuid4())
    return create_model(
        Task, status=TaskStatus(state=TS_SUBMITTED), history=[request],
        task_id=t_id, context_id=c_id, id=t_id
    )


def local_new_agent_text_message(text: str, context_id: str = None, task_id: str = None) -> Message:
    """Creates an Agent Message with safe key mappings."""
    return create_model(
        Message, role=ROLE_AGENT, parts=[make_text_part(text)],
        message_id=str(uuid.uuid4()), task_id=task_id, context_id=context_id
    )


# ==============================================================================
# 3. CORE AGENT LOGIC AND EXECUTION
# ==============================================================================

class HelloWorldAgent:
    """Hello World Agent containing the core business logic."""
    async def invoke(self) -> str:
        return 'Hello, A2A World!'


class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentExecutor Implementation tracking pipeline execution stages."""
    def __init__(self) -> None:
        self.agent = HelloWorldAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        """Executes the agent logic, printing verbose pipeline logs to console."""
        # 1. Initialize or capture the task context
        task = context.current_task or local_new_task(context.message)
        
        # --- DEMO TRACE: Print Received Request ---
        print("\n" + "═" * 80)
        print(f"📥 [A2A DEMO] Received incoming Task Execution Request!")
        print(f"   ├─ Task ID:    {task.id}")
        print(f"   ├─ Context ID: {task.context_id}")
        try:
            # Extract plain text content from the incoming user message safely
            msg_text = "None"
            if context.message and context.message.parts:
                first_part = context.message.parts[0]
                msg_text = getattr(first_part, "text", getattr(getattr(first_part, "root", None), "text", "Unknown"))
            print(f"   └─ Message:    '{msg_text}'")
        except Exception as err:
            print(f"   └─ Message extraction error: {err}")
        print("═" * 80)

        # Enqueue Task Initialization Event
        await event_queue.enqueue_event(task)

        # 2. Track Task status transition to TS_WORKING
        updater = TaskUpdater(event_queue, task.id, task.context_id)
        
        # --- DEMO TRACE: Transition to Working State ---
        print(f"⚙️  [A2A DEMO] Transitioning state -> 'WORKING'...")
        await updater.update_status(
            state=TS_WORKING,
            message=local_new_agent_text_message('Processing request...', task.context_id, task.id),
        )

        # 3. Invoke underlying agent core execution
        print(f"🧠 [A2A DEMO] Invoking HelloWorldAgent core logic...")
        result = await self.agent.invoke()
        print(f"   └─ Agent output payload: '{result}'")

        # 4. Attach generated text output as a structured result artifact
        print(f"📤 [A2A DEMO] Packaging and attaching output artifact ('result')...")
        await updater.add_artifact([make_text_part(result)], name='result')
        
        # 5. Complete task lifecycle
        print(f"✅ [A2A DEMO] Task execution finalized. Sending COMPLETED notification.")
        await updater.complete()
        print("═" * 80 + "\n")

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        print("🛑 [A2A DEMO] Received execution cancel command.")
        raise NotImplementedError('Cancel is not supported')


# ==============================================================================
# 4. SERVER INITIALIZATION & ROUTING
# ==============================================================================

# Create capabilities and skills
capabilities = create_model(AgentCapabilities, streaming=True)
skills = [
    create_model(
        AgentSkill, id="say_hello", name="Say Hello",
        description="Returns a greeting", tags=["hello", "info"], examples=["Say hello"]
    )
]

# Set up supported_interfaces for modern A2A 1.0+ environments
interfaces = []
if AgentInterface is not None:
    interfaces.append(create_model(
        AgentInterface,
        url="http://localhost:10023",
        protocol_binding="JSONRPC"
    ))

# Instantiate the AgentCard using BOTH legacy and modern endpoint specs
hello_world_agent_card = create_model(
    AgentCard,
    name="Hello World A2A Agent",
    description="Simple A2A server implementation",
    version="1.0",
    capabilities=capabilities,
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport="JSONRPC",
    url="http://localhost:10023",          # Resolves on v0.3, discarded on v1.0
    supported_interfaces=interfaces,       # Resolves on v1.0, discarded on v0.3
    skills=skills
)


def create_agent_a2a_server(executor: AgentExecutor, agent_card: AgentCard) -> Starlette:
    """Configures the Starlette application with the dynamic A2A spec routes."""
    app = Starlette()
    
    get_kwargs = lambda func, **fallbacks: {
        k: v for k, v in fallbacks.items() if k in inspect.signature(func).parameters
    }
    
    app.routes.extend([
        *create_agent_card_routes(agent_card, **get_kwargs(create_agent_card_routes, prefix="")),
        *create_jsonrpc_routes(
            DefaultRequestHandler(executor, InMemoryTaskStore(), agent_card),
            **get_kwargs(create_jsonrpc_routes, rpc_url="/", prefix="", enable_v0_3_compat=True, enable_v03_compat=True)
        ),
    ])
    return app


async def run_agent_server(port: int) -> None:
    """Configures and runs the Uvicorn web server instance."""
    config = uvicorn.Config(
        create_agent_a2a_server(HelloWorldAgentExecutor(), hello_world_agent_card),
        host="127.0.0.1", port=port, log_level="info", loop="none"
    )
    await uvicorn.Server(config).serve()


# ==============================================================================
# 5. APPLICATION ENTRYPOINT
# ==============================================================================

def main():
    print("\n" + "═" * 80)
    print("🚀 [A2A DEMO] Starting Hello World Agent on port 10023...")
    print(f"   ├─ Card Name:  {hello_world_agent_card.name}")
    print(f"   ├─ Version:    {hello_world_agent_card.version}")
    print(f"   └─ Endpoints:  GET /.well-known/agent-card.json  |  POST / (JSON-RPC)")
    print("═" * 80 + "\n")
    try:
        asyncio.run(run_agent_server(port=10023))
    except KeyboardInterrupt:
        print("\n🛑 [A2A DEMO] Server stopped manually via KeyboardInterrupt.")
    except Exception as e:
        print(f"\n❌ [A2A DEMO] An error occurred during execution: {e}")


if __name__ == "__main__":
    load_dotenv()
    main()
