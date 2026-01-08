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

import os
import google.auth
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams 

MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp" 
BIGQUERY_MCP_URL = "https://bigquery.googleapis.com/mcp" 
MAPS_API_KEY = os.getenv('MAPS_API_KEY', 'no_api_found')

maps_toolset = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=MAPS_MCP_URL,
        headers={    
            "X-Goog-Api-Key": MAPS_API_KEY
        }
    )
)

root_agent = LlmAgent(
    model='gemini-2.5-flash',
    name='root_agent',
    instruction="""
                You are a specialized assistant for geocoding, based on input you must use 
                **Maps Toolset:** for real-world location analysis, geocoding, geolocation and
                provide answer in a form of a JSON object:
                { 
                    "latitude": "latitude of the location in decimal degrees (string)",
                    "longitude": "longitude of the location in decimal degrees (string)",
                    "accuracy": "accuracy of the location in meters (string)"  
                },
                in case of error provide answer in a form of a JSON object:
                {
                    "error": "error message"
                }
            """,
    tools=[maps_toolset]
)