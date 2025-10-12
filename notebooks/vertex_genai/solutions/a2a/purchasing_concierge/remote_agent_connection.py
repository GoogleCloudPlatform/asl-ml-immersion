from typing import Callable

import httpx

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    SendMessageRequest,
    SendMessageResponse,
    Task,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
)
from uuid import uuid4
from dotenv import load_dotenv
import json
from typing import Any
from a2a.client.errors import (
    A2AClientHTTPError,
    A2AClientJSONError,
    A2AClientTimeoutError,
)
from a2a.client.middleware import ClientCallContext
import requests

load_dotenv()

TaskCallbackArg = Task | TaskStatusUpdateEvent | TaskArtifactUpdateEvent
TaskUpdateCallback = Callable[[TaskCallbackArg, AgentCard], Task]


def _send_request(
    self,
    rpc_request_payload: dict[str, Any],
    http_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Sends a non-streaming JSON-RPC request to the agent.

    Args:
        rpc_request_payload: JSON RPC payload for sending the request.
        http_kwargs: Optional dictionary of keyword arguments to pass to the
            underlying post request.

    Returns:
        The JSON response payload as a dictionary.

    Raises:
        A2AClientHTTPError: If an HTTP error occurs during the request.
        A2AClientJSONError: If the response body cannot be decoded as JSON.
    """
    try:
        response = requests.post(
            self.url, json=rpc_request_payload, **(http_kwargs or {})
        )
        response.raise_for_status()
        return response.json()
    except httpx.ReadTimeout as e:
        raise A2AClientTimeoutError("Client Request timed out") from e
    except httpx.HTTPStatusError as e:
        raise A2AClientHTTPError(e.response.status_code, str(e)) from e
    except json.JSONDecodeError as e:
        raise A2AClientJSONError(str(e)) from e
    except httpx.RequestError as e:
        raise A2AClientHTTPError(503, f"Network communication error: {e}") from e


def send_message(
    self,
    request: SendMessageRequest,
    *,
    http_kwargs: dict[str, Any] | None = None,
    context: ClientCallContext | None = None,
) -> SendMessageResponse:
    """Sends a non-streaming message request to the agent.

    Args:
        request: The `SendMessageRequest` object containing the message and configuration.
        http_kwargs: Optional dictionary of keyword arguments to pass to the
            underlying httpx.post request.
        context: The client call context.

    Returns:
        A `SendMessageResponse` object containing the agent's response (Task or Message) or an error.

    Raises:
        A2AClientHTTPError: If an HTTP error occurs during the request.
        A2AClientJSONError: If the response body cannot be decoded as JSON or validated.
    """
    if not request.id:
        request.id = str(uuid4())

    response_data = self._send_request(
        request.model_dump(mode="json", exclude_none=True), http_kwargs
    )
    return SendMessageResponse.model_validate(response_data)


class RemoteAgentConnections:
    """A class to hold the connections to the remote agents."""

    def __init__(self, agent_card: AgentCard, agent_url: str):
        print(f"agent_card: {agent_card}")
        print(f"agent_url: {agent_url}")
        self._httpx_client = httpx.AsyncClient(timeout=30)
        self.agent_client = A2AClient(self._httpx_client, agent_card, url=agent_url)

        # Replace the original method with our custom implementation
        # NOTE: This is a temporary workaround for issue in httpx event closed
        self.agent_client._send_request = _send_request.__get__(self.agent_client)
        self.agent_client.send_message = send_message.__get__(self.agent_client)

        self.card = agent_card

    def get_agent(self) -> AgentCard:
        return self.card

    def send_message(self, message_request: SendMessageRequest) -> SendMessageResponse:
        return self.agent_client.send_message(message_request)
