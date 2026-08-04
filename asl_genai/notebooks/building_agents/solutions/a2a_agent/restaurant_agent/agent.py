# restaurant_agent/agent.py
import os
import re

import httpx
from a2a.types import AgentCard, AgentInterface
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.auth import default
from google.auth.transport.requests import Request

RESERVATION_AGENT_CARD_URL = os.environ.get("RESERVATION_AGENT_CARD_URL", "")


def search_menu(cuisine_type: str = "") -> str:
    """Search restaurant menu items by cuisine type."""
    return f"Menu items for {cuisine_type or 'all cuisines'}: Margherita Pizza, Spaghetti Carbonara, Tiramisu."


def get_gcp_httpx_client(timeout: int = 60) -> httpx.AsyncClient:
    credentials, _ = default(
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    if not credentials.valid:
        credentials.refresh(Request())
    return httpx.AsyncClient(
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=timeout,
    )


agent_card = AgentCard(
    name="reservation_agent",
    description="Handles restaurant table reservations — create, check, and cancel bookings.",
    supported_interfaces=[
        AgentInterface(
            url=RESERVATION_AGENT_CARD_URL,
            protocol_binding="HTTP+JSON",
            protocol_version="1.0",
        )
    ],
    skills=[],
)

reservation_remote_agent = RemoteA2aAgent(
    name="reservation_agent",
    description="Handles restaurant table reservations — create, check, and cancel bookings. Delegate to this agent when the user wants to book a table, check a reservation, or cancel a reservation.",
    agent_card=agent_card,
    httpx_client=get_gcp_httpx_client(),
)


root_agent = LlmAgent(
    name="restaurant_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        client_kwargs={"vertexai": True, "location": "global"},
    ),
    instruction="""You are a friendly and knowledgeable concierge at "Foodie Finds," a restaurant. Your job:
- Help diners browse the menu by category or cuisine type.
- Provide full details about specific dishes, including ingredients, price, and dietary information.
- Recommend dishes based on natural language descriptions of what the diner is craving.
- Add new menu items when asked.
- For reservation requests (booking, checking, or cancelling tables), call the reservation_agent.

When a diner asks about a specific dish by name or cuisine, use the menu tools.
For any reservation requests, always delegate to the reservation_agent.
Be conversational, knowledgeable, and concise.""",
    tools=[search_menu, AgentTool(reservation_remote_agent)],
    # sub_agents=[reservation_remote_agent],
)
