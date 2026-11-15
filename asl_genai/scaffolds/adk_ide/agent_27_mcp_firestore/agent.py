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
from google.adk.agents import Agent
import os
import google.auth
from google.auth.transport.requests import Request

from google.adk import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset, StreamableHTTPConnectionParams
from google.adk.runners import InMemoryRunner, print_event
from google.genai import types

# Set your project configuration
PROJECT_ID = os.environ.get("PROJECT_ID", "my-project-id")
DOC_DATASET_ID = os.environ.get("DOC_DATASET_ID", "my-db-id")
MODEL = "gemini-2.5-flash"

# Authenticate and get token
credentials, _ = google.auth.default()
credentials.refresh(Request())

# Configure the Firestore remote MCP server
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://firestore.googleapis.com/mcp",
        headers={
            "Accept": "text/event-stream, application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {credentials.token}"
        },
    ),
)

root_agent = Agent(
    name="mcp_codelab_agent",
    model=MODEL,
    instruction=f"""You are a Firestore database assistant. 
    Use the available Firestore MCP tools to query, retrieve, 
    and manage documents in the database based on the user's request.
    use project_id={PROJECT_ID} and database_id="{DOC_DATASET_ID}",
    use parent path: "projects/{PROJECT_ID}/databases/{DOC_DATASET_ID}/documents"
    """,
    tools=[mcp_toolset],
)
