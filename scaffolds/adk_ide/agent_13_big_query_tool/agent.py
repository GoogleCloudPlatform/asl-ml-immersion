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

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.bigquery import BigQueryCredentialsConfig
from google.adk.tools.bigquery import BigQueryToolset
from google.adk.tools.bigquery.config import BigQueryToolConfig
from google.adk.tools.bigquery.config import WriteMode
from google.genai import types
import google.auth

# Define constants for this example agent
AGENT_NAME = "bigquery_agent"
APP_NAME = "bigquery_app"
USER_ID = "user1234"
SESSION_ID = "1234"
GEMINI_MODEL = "gemini-2.0-flash"

# Define a tool configuration to block any write operations
tool_config = BigQueryToolConfig(write_mode=WriteMode.BLOCKED)

# Uses externally-managed Application Default Credentials (ADC) by default.
# This decouples authentication from the agent / tool lifecycle.
# https://cloud.google.com/docs/authentication/provide-credentials-adc
credentials_config = BigQueryCredentialsConfig()



# Instantiate a BigQuery toolset
bigquery_toolset = BigQueryToolset(
    credentials_config=credentials_config, bigquery_tool_config=tool_config
)

# Agent Definition
bigquery_agent = Agent(
    model=GEMINI_MODEL,
    name=AGENT_NAME,
    description=(
        "Agent to answer questions about BigQuery data and models and execute"
        " SQL queries."
    ),
    instruction="""\
        You are a data science agent with access to several BigQuery tools.
        Make use of those tools to answer the user's questions.
    """,
    tools=[bigquery_toolset],
)

root_agent = bigquery_agent

# # Session and Runner
# session_service = InMemorySessionService()
# session = asyncio.run(
#     session_service.create_session(
#         app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
#     )
# )
# runner = Runner(
#     agent=bigquery_agent, app_name=APP_NAME, session_service=session_service
# )


# # Agent Interaction
# def call_agent(query):
#     """
#     Helper function to call the agent with a query.
#     """
#     content = types.Content(role="user", parts=[types.Part(text=query)])
#     events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

#     print("USER:", query)
#     for event in events:
#         if event.is_final_response():
#             final_response = event.content.parts[0].text
#             print("AGENT:", final_response)


# call_agent("Are there any ml datasets in bigquery-public-data project?")
# call_agent("Tell me more about ml_datasets.")
# call_agent("Which all tables does it have?")
# call_agent("Tell me more about the census_adult_income table.")
# call_agent("How many rows are there per income bracket?")
# call_agent(
#     "What is the statistical correlation between education_num, age, and the income_bracket?"
# )