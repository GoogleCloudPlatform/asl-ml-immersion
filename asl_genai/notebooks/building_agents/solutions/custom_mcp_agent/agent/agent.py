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

"""Example of using MCP Toolset to create an inventory management tool."""

import os

import google.auth.transport.requests
import google.oauth2.id_token
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

# Load environment variables from .env file
env_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".env")
)
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    load_dotenv(override=True)

MODEL = "gemini-3.5-flash"

# Connect to the remote Cloud Run MCP Server over HTTPS
MCP_SERVER_URL = os.environ.get(
    "REMOTE_MCP_SERVER_URL",
    "https://inventory-mcp-server-xxxxxxxx-uc.a.run.app/sse",
)

# Fetch OIDC ID Token for Cloud Run IAM authentication if accessing over HTTPS
headers = {}
if MCP_SERVER_URL.startswith("https://"):
    try:
        audience = MCP_SERVER_URL.split("/sse")[0].rstrip("/")
        auth_req = google.auth.transport.requests.Request()
        token = google.oauth2.id_token.fetch_id_token(
            auth_req, audience=audience
        )
        headers["Authorization"] = f"Bearer {token}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(
            "Warning: Could not fetch ID token for Cloud Run"
            f" authentication: {e}"
        )

root_agent = LlmAgent(
    model=Gemini(
        model=MODEL,
        client_kwargs={"vertexai": True, "location": "global"},
    ),
    name="inventory_assistant",
    description="You are a specialized assistant for inventory management.",
    instruction=(
        "Help user get answer to their queries about inventory and update "
        "or process the items."
    ),
    tools=[
        McpToolset(
            connection_params=SseServerParams(
                url=MCP_SERVER_URL,
                headers=headers if headers else None,
            ),
        )
    ],
)
