import asyncio
from contextlib import AsyncExitStack
from uuid import uuid4

import click
from google.adk.agents import Agent, LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_session_manager import (
    SseServerParams,
    StdioConnectionParams,
)
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.genai import types
from pydantic import BaseModel

MODEL = "gemini-2.5-flash"
MCP_SERVER_URL = "http://0.0.0.0:4200/inventory"

root_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="inventory_assistant",
    description="You are a specialized assistant for inventory management.",
    instruction=(
        "Help user get answer to their queries about inventory and update "
        "the items."
    ),
    tools=[
        McpToolset(
            connection_params=SseServerParams(url=MCP_SERVER_URL),
        )
    ],
)