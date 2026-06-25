# pylint: skip-file

import os

import google.auth
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)

# ADK MCP imports
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.auth.transport.requests import Request

BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT")


def get_bigquery_mcp_toolset() -> MCPToolset:
    """
    Create an MCPToolset connected to Google's managed BigQuery MCP server.
    """
    # Get OAuth credentials
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    credentials.refresh(Request())
    oauth_token = credentials.token

    # Use environment project if available
    if PROJECT_ID:
        project_id = PROJECT_ID

    # Create headers with OAuth token
    headers = {
        "Authorization": f"Bearer {oauth_token}",
        "x-goog-user-project": project_id,
    }

    # Create the MCPToolset
    tools = MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers=headers,
        )
    )

    print(f"[BigQueryTools] MCP Toolset configured for project: {project_id}")

    return tools
