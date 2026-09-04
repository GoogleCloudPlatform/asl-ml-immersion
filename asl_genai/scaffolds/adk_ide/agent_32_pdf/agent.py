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
from typing import Any, Dict, Optional

from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import Agent
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from google.adk.tools import load_artifacts

MODEL = "gemini-2.5-flash"

from google.adk.tools.tool_context import ToolContext
from google.genai import types

async def save_artifact(tool_context: ToolContext, file_content: str, filename : str):
    data_bytes = file_content.encode("utf-8")
    artifact_part = types.Part(
        inline_data=types.Blob(mime_type='text/plain', data=data_bytes)
    )
    await tool_context.save_artifact(filename, artifact_part)
    
root_agent = Agent(
    name = "artifacts_agent",
    description = "Agent to work with artifacts",
instruction="""
        You are a helpful assistant to work with artifacts (files).
        1.  When the user asks you to create any content (report, document, etc), you MUST then call the 
            'save_artifact' tool with the full content to save it as an artifact.
        2.  In case of any questions about previously saved artifacts, you MUST use the 'load_artifacts' 
            tool to retrieve them.
    """,
    model = MODEL,
    tools = [save_artifact, load_artifacts]
)