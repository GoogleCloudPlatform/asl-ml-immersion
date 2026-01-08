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

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

MODEL = "gemini-2.0-flash"

from .tools import get_weather

weather_agent = Agent(
    name="weather_agent_v2",  # Give it a new version name
    model=MODEL,
    description="Handles weather information requests using the 'get_weather' tool.",
    instruction="You are the Weather Agent. Your primary responsibility is to provide weather information. "
    "Use the 'get_weather' tool for weather requests (e.g., 'weather in London'). "
    "Do not perform any other actions.",
    tools=[get_weather],
)
root_agent = weather_agent

# Make the agent A2A-compatible
a2a_app = to_a2a(root_agent, port=10020)