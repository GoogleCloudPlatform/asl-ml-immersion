
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

from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langchain_google_vertexai import ChatVertexAI
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition

# --- 1. Define State & Tools (Module Level) ---
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

@tool
def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city."""
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": "The weather in New York is sunny with a temperature of 25°C."
        },
        "london": {
            "status": "success",
            "report": "It's cloudy in London with a temperature of 15°C."
        },
        "tokyo": {
            "status": "success",
            "report": "Tokyo is experiencing light rain and a temperature of 18°C."
        },
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    return {
        "status": "error",
        "error_message": f"Sorry, I don't have weather information for '{city}'."
    }

# --- 2. Class Definition ---

class LangGraphWeatherAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """
        Initialize the agent with a model and build the graph.
        """
        # 1. Setup Model and Tools
        self.tools = [get_weather]
        self.llm = ChatVertexAI(model=model_name)
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 2. Define System Instructions
        self.system_instruction = (
            "You are a helpful weather assistant. "
            "When the user asks for the weather in a specific city, "
            "use the 'get_weather' tool to find the information. "
            "If the tool returns an error, inform the user politely. "
            "If the tool is successful, present the weather report clearly."
        )

        # 3. Build and Compile the Graph
        self.graph = self._build_graph()

    def _agent_node(self, state: AgentState):
        """
        Internal node function to invoke the model.
        """
        messages = state["messages"]
        
        # Prepend system message if not present
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=self.system_instruction)] + messages
            
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def _build_graph(self):
        """
        Constructs the StateGraph with nodes and edges.
        """
        builder = StateGraph(AgentState)
        
        # Define Nodes
        builder.add_node("agent", self._agent_node)
        builder.add_node("tools", ToolNode(self.tools))
        
        # Define Edges
        builder.add_edge(START, "agent")
        builder.add_conditional_edges("agent", tools_condition)
        builder.add_edge("tools", "agent")
        
        return builder.compile()

    def invoke(self, user_query: str) -> Dict[str, Any]:
        """
        Public method to run the agent.
        """
        initial_state = {"messages": [HumanMessage(content=user_query)]}
        result = self.graph.invoke(initial_state)
        return result

# --- A2A Executor Implementation ---
class LangGraphExecutor(AgentExecutor):
    """
    Orchestrates the LangGraph agent execution within the A2A server context.
    """
    def __init__(self, agent: LangGraphWeatherAgent):
        self.agent = agent

    def _reconstruct_history(self, context: RequestContext) -> List[BaseMessage]:
        """
        Reconstructs LangChain messages from the A2A task history.
        """
        messages = []
        messages.append(SystemMessage(content="You are a helpful weather assistant."))

        # Extract the current user message
        user_input = ""
        if hasattr(context, "message") and context.message:
            msg = context.message
            if hasattr(msg, "content") and msg.content:
                user_input = msg.content
            elif hasattr(msg, "parts") and msg.parts:
                texts = []
                for part in msg.parts:
                    if hasattr(part, "text") and part.text:
                        texts.append(part.text)
                    elif hasattr(part, "root") and hasattr(part.root, "text"):
                        texts.append(part.root.text)
                user_input = "\n".join(texts)
            
            if not user_input:
                user_input = str(msg)
        else:
            user_input = "Hello"
            
        messages.append(HumanMessage(content=user_input))
        return messages

    async def execute(self, context: RequestContext, event_queue: EventQueue):
        logger.info(f"Starting execution for Task ID: {context.task_id}")
        
        # 1. Reconstruct State
        inputs = {"messages": self._reconstruct_history(context)}
        
        final_response = "No response generated."
        
        # 2. Stream execution
        async for output in self.agent.graph.astream(inputs):
            for node_name, state_update in output.items():
                if "messages" in state_update:
                    msgs = state_update["messages"]
                    if msgs:
                        last_msg = msgs[-1]
                        if isinstance(last_msg, AIMessage) and not last_msg.tool_calls:
                            final_response = last_msg.content

        logger.info(f"Final response: {final_response}")

        # 3. Resolve Status
        parts = [Part(root=TextPart(text=str(final_response)))]
        update_event = completed_task(
                    context.task_id,
                    context.context_id,
                    [new_artifact(parts, f"weather_{context.task_id}")],
                    [context.message],
                )
        
        await event_queue.enqueue_event(update_event)

    async def cancel(self, task_id: str) -> None:
        """
        Handles task cancellation requests from the server.
        """
        logger.info(f"Cancellation requested for task {task_id}")
        # In a more complex implementation, you would trigger a flag
        # to break the 'async for' loop in execute().
        pass

# --- Server Setup ---

weather_agent_card = AgentCard(
    name="Weather Agent LangGraph",
    url="http://localhost:10022",
    description="Provides weather information using LangGraph",
    version="1.0",
    capabilities=AgentCapabilities(streaming=True),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    preferred_transport=TransportProtocol.jsonrpc,
    skills=[
        AgentSkill(
            id="get_weather",
            name="Get Weather",
            description="Provides weather reports for major cities",
            tags=["weather", "info"],
            examples=["Weather in London", "Is it raining in Tokyo?"],
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
    agent_logic = LangGraphWeatherAgent(model_name="gemini-2.0-flash")
    executor = LangGraphExecutor(agent=agent_logic)
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
    print("Starting LangGraph Weather Agent...")
    try:
        asyncio.run(run_agent_server(port=10022))
    except KeyboardInterrupt:
        print("\nServer stopped manually.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()