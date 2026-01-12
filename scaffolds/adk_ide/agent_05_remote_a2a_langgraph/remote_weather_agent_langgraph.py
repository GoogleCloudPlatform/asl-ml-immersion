
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
import uuid
from typing import TypedDict, List, Annotated, Union, Dict, Any, Literal
import operator

import uvicorn
from dotenv import load_dotenv

# A2A Imports
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.request_handlers.default_request_handler import RequestContext
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.events import EventQueue
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    TransportProtocol,
    TaskStatus,
    TaskStatusUpdateEvent,
)

# LangGraph Imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

# Tools
from .tools import get_weather

load_dotenv()

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("weather_agent_langgraph")

# --- LangGraph Setup ---

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

def get_weather_tool_check(query: str):
    """
    Simple deterministic logic to mimic model decision for "weather" tool.
    Extracts city from queries like "weather in London" or "what is the weather in Paris".
    """
    query = query.lower()
    if "weather" in query:
        words = query.split()
        if "in" in words:
            try:
                city_idx = words.index("in") + 1
                if city_idx < len(words):
                    city = words[city_idx].strip("?.")
                    return {"name": "get_weather", "args": {"city": city}}
            except Exception:
                pass
    return None

async def model_node(state: AgentState):
    """
    Simulates a model that decides whether to call a tool or reply directly.
    """
    messages = state["messages"]
    last_msg = messages[-1]
    
    # helper to get text content
    text = ""
    if hasattr(last_msg, "content"):
        text = last_msg.content
    else:
        text = str(last_msg)

    logger.info(f"Model processing: {text}")
    
    # Check if we should call tool
    tool_call = get_weather_tool_check(text)
    
    if tool_call:
        logger.info(f"Decided to call tool: {tool_call}")
        return {"messages": [AIMessage(
            content="",
            tool_calls=[{
                "name": tool_call["name"],
                "args": tool_call["args"],
                "id": str(uuid.uuid4())
            }]
        )]}
    
    # If it was a ToolMessage essentially we just got the result,
    # so we should formulate a final response.
    # But wait, this node is also the "entry" node.
    if isinstance(last_msg, ToolMessage):
        # We just got tool output, return final answer based on it
        return {"messages": [AIMessage(content=f"Here is the weather info: {last_msg.content}")]}
        
    # Default chat response
    return {"messages": [AIMessage(content=f"I am a weather agent. I can only help with weather requests (e.g., 'weather in London').")]}

def tool_node(state: AgentState):
    """
    Executes tools requested by the model.
    """
    messages = state["messages"]
    last_msg = messages[-1]
    
    results = []
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        for tool_call in last_msg.tool_calls:
            if tool_call["name"] == "get_weather":
                try:
                    res = get_weather(tool_call["args"]["city"])
                    content = str(res)
                except Exception as e:
                    content = f"Error: {e}"
                
                results.append(ToolMessage(
                    tool_call_id=tool_call["id"],
                    content=content,
                    name=tool_call["name"]
                ))
    
    return {"messages": results}

def should_continue(state: AgentState):
    messages = state["messages"]
    last_msg = messages[-1]
    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        return "tools"
    return END

# Build Graph
workflow = StateGraph(AgentState)
workflow.add_node("agent", model_node)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent") # Loop back to agent to generate final response

app_graph = workflow.compile()


# --- A2A Executor Adapter ---

class LangGraphExecutor:
    """
    Adapts LangGraph execution to the A2A Executor interface used by DefaultRequestHandler.
    """
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        logger.info(f"Executing task {context.task_id}")
        
        user_input = "Hello"
        if hasattr(context, "message") and context.message:
            msg = context.message
            if hasattr(msg, "content"):
                user_input = msg.content
            elif isinstance(msg, dict):
                user_input = msg.get("content", str(msg))
            else:
                user_input = str(msg)
        
        logger.info(f"User input: {user_input}")

        # Initial State
        inputs = {"messages": [HumanMessage(content=user_input)]}
        
        final_response = "No response generated."
        
        # Run graph
        async for output in app_graph.astream(inputs):
            for key, value in output.items():
                if "messages" in value:
                    msgs = value["messages"]
                    if msgs:
                        last = msgs[-1]
                        if isinstance(last, AIMessage) and not last.tool_calls:
                            final_response = last.content
        
        logger.info(f"Final response: {final_response}")

        # Send completion event
        # Try to use TaskStatus.COMPLETED if available, else string
        status = "completed"
        if hasattr(TaskStatus, "COMPLETED"):
            status = TaskStatus.COMPLETED
            
        update_event = TaskStatusUpdateEvent(
            task_id=context.task_id,
            status=status,
            result=final_response
        )
        
        await event_queue.enqueue_event(update_event)


# --- Server Function definitions ---

weather_agent_card = AgentCard(
    name="Weather Agent LangGraph",
    url="http://localhost:10021",
    description="Provides weather information via LangGraph",
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

def create_agent_a2a_server(executor, agent_card):
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    return A2AStarletteApplication(
        agent_card=agent_card, http_handler=handler
    )

async def run_agent_server(port) -> None:
    executor = LangGraphExecutor()
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
    print("Starting LangGraph agent server")
    try:
        asyncio.run(run_agent_server(port=10021))
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
