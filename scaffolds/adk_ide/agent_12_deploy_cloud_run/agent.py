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
This is a simple example of using MCP Toolset
to create a tool for inventory management.
"""
from google.adk.agents import Agent

from .tools import get_pycon_events

MODEL = "gemini-2.0-flash"

root_agent = Agent(
    name="pycon_agent_v1",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="Provides information about PyCon events for specific cities.",
    instruction="""
    You are an expert **PyCon Events Suggestion Assistant**.

    When the user requests **event suggestions** for a **specific city and date range**,
    you must use the **'get_pycon_events' tool** to find relevant information.

    If the tool returns an error or no events are found, **inform the user politely** that you could not find any events or that there might be an issue.

    If the tool is successful and returns events, **present the event suggestions clearly**, including the **event name, date, and a brief description** if available.
    """,
    tools=[get_pycon_events],  # Pass the function directly
)
