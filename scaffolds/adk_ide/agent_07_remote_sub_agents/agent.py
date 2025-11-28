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

from google.adk.agents import Agent, SequentialAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

AGENT_CARD_WELL_KNOWN_PATH = "/.well-known/agent-card.json"

remote_trending_agent = RemoteA2aAgent(
    name="find_trends",
    description="Searches for current trending topics on social media",
    agent_card=f"http://localhost:10020{AGENT_CARD_WELL_KNOWN_PATH}",
)

remote_analyzer_agent = RemoteA2aAgent(
    name="analyze_trends",
    description="Provides quantitative analysis of a specific trend",
    agent_card=f"http://localhost:10021{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Create the Host ADK Agent
host_agent = SequentialAgent(
    name="trend_analysis_host",
    sub_agents=[remote_trending_agent, remote_analyzer_agent],
)
root_agent = host_agent
