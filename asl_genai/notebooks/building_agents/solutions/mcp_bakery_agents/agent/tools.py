# pylint: skip-file
import os

import dotenv
import google.auth
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp"


def get_maps_mcp_toolset():
    maps_api_key = os.getenv("MAPS_API_KEY", "YOUR_MAPS_API_KEY")
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={"X-Goog-Api-Key": maps_api_key},
            timeout=30.0,
            sse_read_timeout=300.0,
        )
    )


def get_bigquery_mcp_toolset():
    credentials, project_id = google.auth.default(
        scopes=["https://www.googleapis.com/auth/bigquery"]
    )
    credentials.refresh(google.auth.transport.requests.Request())
    oauth_token = credentials.token
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=BIGQUERY_MCP_URL,
            headers={
                "Authorization": f"Bearer {oauth_token}",
                "x-goog-user-project": project_id,
            },
            timeout=30.0,
            sse_read_timeout=300.0,
        )
    )
