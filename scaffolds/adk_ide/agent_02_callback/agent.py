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
from google.adk.agents.llm_agent import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai.types import Content, Part
from typing import Any, Dict, Optional

MODEL = "gemini-2.0-flash"

from .tools import get_location, get_weather

# Before Agent Callback
# Ideal for logging, pre-execution validation checks, or skipping agent execution.
def before_agent_callback(callback_context: CallbackContext) -> Optional[Content]:

    print(f"!!! before_agent_callback")
    print(f"  Agent: {callback_context.agent_name}")
    print(f"  Invocation ID: {callback_context.invocation_id}")
    print(f"  Current State: {callback_context.state.to_dict()}")

    # Allow default behavior
    return None


# After Agent Callback
# Ideal for logging, post-execution validation checks, or modifying/augmenting final response.
def after_agent_callback(callback_context: CallbackContext) -> Optional[Content]:

    print(f"!!! after_agent_callback")
    print(f"  Agent: {callback_context.agent_name}")
    print(f"  Invocation ID: {callback_context.invocation_id}")
    print(f"  Current State: {callback_context.state.to_dict()}")

    # Allow default behavior
    return None


# Before Model Callback
# Ideal for logging, inspection/modification of LlmRequest, or skipping model call.
def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:

    print(f"!!! before_model_callback")
    print(f"  Agent: {callback_context.agent_name}")
    print(f"  Invocation ID: {callback_context.invocation_id}")

    # Inspect the last user message in the request
    test = False
    if test:
        last_user_message = ""
        if llm_request.contents and llm_request.contents[-1].role == "user":
            if llm_request.contents[-1].parts:
                last_user_message = llm_request.contents[-1].parts[0].text
        print(f"  Inspecting last user message: '{last_user_message}'")

    # Return LlmResponse to skip model call
    if test:
        print(f"  Model call skipped")
        return LlmResponse(
            content=Content(
                parts=[Part(text=f"Model call skipped by 'before_model_callback'.")],
                role="model",  # Assign model role to the overriding response
            )
        )
    # Allow default behavior
    return None


# After Model Callback
# Ideal for logging, inspection/modification of LlmResponse.
def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:

    print(f"!!! after_model_callback")
    print(f"  Agent: {callback_context.agent_name}")
    print(f"  Invocation ID: {callback_context.invocation_id}")

    # Inspect the model response
    test = False
    if test:
        response_text = ""
        if llm_response.content and llm_response.content.parts:
            response_text = llm_response.content.parts[0].text
        print(f"  Inspecting model response: '{response_text}'")

    # Modify the model response with a new LlmResponse
    if test:
        print(f"  Model response modified to be uppercase")
        modified_response = LlmResponse(
            content=Content(
                parts=[
                    Part(
                        text=f"[Modified by after_model_callback] {llm_response.content.parts[0].text.upper()}"
                    )
                ],
                role="model",
            )
        )
        return modified_response

    # Allow default behavior
    return None


# Before Tool Callback
# Ideal for logging, inspection/modification of tool args, or skipping tool execution.
def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:

    print(f"!!! before_tool_callback")
    print(f"  Agent: {tool_context.agent_name}")
    print(f"  Invocation ID: {tool_context.invocation_id}")
    print(f"  Tool: {tool.name}")
    print(f"  Args: {args}")

    # Return tool response to skip tool execution
    test = True
    if test:
        if tool.name == "get_weather" and args.get("city").lower() == "dublin":
            tool_response = "The weather in Dublin is always rainy."
            print(
                f"  Tool execution skipped for location Dublin and returning tool response: {tool_response}"
            )
            return tool_response

    # Allow default behavior
    return None


# After Tool Callback
# Ideal for logging, inspection/modification of tool response.
def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:

    print(f"!!! after_tool_callback")
    print(f"  Agent: {tool_context.agent_name}")
    print(f"  Invocation ID: {tool_context.invocation_id}")
    print(f"  Tool: {tool.name}")
    print(f"  Args: {args}")
    print(f"  Tool response: {tool_response}")

    # Modify the tool response
    test = False
    if test:
        if tool.name == "get_weather":
            tool_response = "The weather is always rainy and gloomy."
            print(f"  Tool response modified for 'get_weather' to: {tool_response}")
            return tool_response

    # Allow default behavior
    return None

root_agent = Agent(
    name="weather_agent_v2",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="""Provides weather information for specific
    cities based on your location""",
    instruction="""You are a helpful weather assistant.
    When the user asks for the weather in a specific city,
    use the 'get_weather' tool to find the information.
    If user doesnt specify a city, use the 'get_location' tool to find the information.
    If the tool returns an error, inform the user politely.
    If the tool is successful, present the weather report clearly.""",
    tools=[get_location, get_weather],
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)


