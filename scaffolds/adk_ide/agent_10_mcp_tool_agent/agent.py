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

"""
This is a simple example of using MCP Toolset to create a tool for inventory management.
"""
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

# TODO: IMPORTANT! Change the path below to your remote MCP Server path
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
