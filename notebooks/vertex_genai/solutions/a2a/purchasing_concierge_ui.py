"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import gradio as gr

from typing import List, Dict, Any
from pprint import pformat
from vertexai import agent_engines
import os
from dotenv import load_dotenv

load_dotenv()

USER_ID = "default_user"

REMOTE_APP = agent_engines.get(os.getenv("AGENT_ENGINE_RESOURCE_NAME"))
SESSION_ID = REMOTE_APP.create_session(user_id=USER_ID)["id"]


async def get_response_from_agent(
    message: str,
    history: List[Dict[str, Any]],
) -> str:
    """Send the message to the backend and get a response.

    Args:
        message: Text content of the message.
        history: List of previous message dictionaries in the conversation.

    Returns:
        Text response from the backend service.
    """
    # try:

    default_response = "No response from agent"

    responses = []

    for event in REMOTE_APP.stream_query(
        user_id=USER_ID,
        session_id=SESSION_ID,
        message=message,
    ):
        parts = event.get("content", {}).get("parts", [])
        if parts:
            for part in parts:
                if part.get("function_call"):
                    formatted_call = f"```python\n{pformat(part.get('function_call'), indent=2, width=80)}\n```"
                    responses.append(
                        gr.ChatMessage(
                            role="assistant",
                            content=f"{part.get('function_call').get('name')}:\n{formatted_call}",
                            metadata={"title": "🛠️ Tool Call"},
                        )
                    )
                elif part.get("function_response"):
                    formatted_response = f"```python\n{pformat(part.get('function_response'), indent=2, width=80)}\n```"

                    responses.append(
                        gr.ChatMessage(
                            role="assistant",
                            content=formatted_response,
                            metadata={"title": "⚡ Tool Response"},
                        )
                    )
                elif part.get("text"):
                    responses.append(
                        gr.ChatMessage(
                            role="assistant",
                            content=part.get("text"),
                        )
                    )
                else:
                    formatted_unknown_parts = f"Unknown agent response part:\n\n```python\n{pformat(part, indent=2, width=80)}\n```"

                    responses.append(
                        gr.ChatMessage(
                            role="assistant",
                            content=formatted_unknown_parts,
                        )
                    )

    if not responses:
        yield default_response

    yield responses


if __name__ == "__main__":
    demo = gr.ChatInterface(
        get_response_from_agent,
        title="Purchasing Concierge",
        description="This assistant can help you to purchase food from remote sellers.",
        type="messages",
    )

    demo.launch(
        server_name="0.0.0.0",
        server_port=8080,
    )
