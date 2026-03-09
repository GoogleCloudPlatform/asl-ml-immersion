# pylint: skip-file

import os

from google.adk.agents import LlmAgent

# Import implementations
from .guards.modelarmor_callbacks import ModelArmorGuard
from .prompt import PROMPT
from .tools.bigquery_tools import get_bigquery_mcp_toolset

MODELARMOR_TEMPLATE_NAME = os.environ.get("MODELARMOR_TEMPLATE_NAME")
GOOGLE_CLOUD_LOCATION = os.environ.get("GOOGLE_CLOUD_LOCATION")

# Create the BigQuery MCP toolset
bigquery_tools = get_bigquery_mcp_toolset()

# Create the Model Armor guard
model_armor_guard = ModelArmorGuard(
    template_name=MODELARMOR_TEMPLATE_NAME, location=GOOGLE_CLOUD_LOCATION
)

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="customer_service_agent",
    instruction=PROMPT,
    tools=[bigquery_tools],
    before_model_callback=model_armor_guard.before_model_callback,
    after_model_callback=model_armor_guard.after_model_callback,
)
