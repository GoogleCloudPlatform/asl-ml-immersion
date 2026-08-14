# pylint: skip-file
import os

from google.adk.agents import LlmAgent

from . import tools

bq_toolset = tools.get_bigquery_mcp_toolset()
maps_toolset = tools.get_maps_mcp_toolset()

PROJECT_ID = os.getenv("PROJECT_ID")

PROMPT = f"""
You are a helpful business consultant helping a friend launch a new high-end sourdough bakery in Los Angeles.
Your goal is to recommend the best neighborhood and a premium price point.

To do this, you should:
1. Query BigQuery mcp_bakery dataset under {PROJECT_ID} project to find neighborhoods with high bachelors degree percentage and high foot traffic index (macro trends).
2. Query BigQuery mcp_bakery dataset under {PROJECT_ID} project to analyze competitor pricing for 'Sourdough Loaf' in 'Los Angeles Metro' to suggest a premium price.
3. Use Google Maps tools to validate micro-location details or search for specific locations in the chosen neighborhood.

Google Cloud project ID:
{PROJECT_ID}

Be strategic and combine insights from both sources.
"""

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="bakery_consultant_agent",
    instruction=PROMPT,
    tools=[bq_toolset, maps_toolset],
)
