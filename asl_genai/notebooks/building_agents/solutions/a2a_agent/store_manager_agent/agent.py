# store_manager_agent/agent.py
"""Store Manager Agent module for A2A integration."""

import os

import httpx
from a2a.types import AgentCard, AgentInterface
from google.adk.agents import LlmAgent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.auth import default
from google.auth.transport.requests import Request as AuthRequest

INVENTORY_AGENT_CARD_URL = os.environ.get("INVENTORY_AGENT_CARD_URL", "")


def get_store_info(info_type: str = "hours") -> str:
    """Get general store information like operating hours or contact details."""
    if "hour" in str(info_type).lower():
        return (
            "Store hours: Monday-Saturday 8:00 AM - 9:00 PM, "
            "Sunday 10:00 AM - 6:00 PM."
        )
    if "contact" in str(info_type).lower():
        return (
            "Store contact: support@store.example.com, Phone: (555) 019-2834."
        )
    return "Store location: 123 Main Street, Suite 100."


def get_gcp_httpx_client(timeout: int = 60) -> httpx.AsyncClient:
    """Create an authenticated HTTP client using ADC."""
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]
    credentials, _ = default(scopes=scopes)
    if not credentials.valid:
        credentials.refresh(AuthRequest())
    return httpx.AsyncClient(
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=timeout,
    )


# Define remote A2A sub-agent if URL is configured
agent_card = AgentCard(
    name="inventory_assistant",
    description=(
        "Specialized assistant for inventory management, listing SKUs, "
        "and updating stock quantities."
    ),
    supported_interfaces=[
        AgentInterface(
            url=INVENTORY_AGENT_CARD_URL,
            protocol_binding="HTTP+JSON",
            protocol_version="1.0",
        )
    ],
    skills=[],
)

inventory_remote_agent = RemoteA2aAgent(
    name="inventory_assistant",
    description=(
        "Specialized assistant for inventory management, listing SKUs, "
        "and updating stock quantities. Delegate to this agent for any "
        "inventory or stock operations."
    ),
    agent_card=agent_card,
    httpx_client=get_gcp_httpx_client(),
)


root_agent = LlmAgent(
    name="store_manager_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        client_kwargs={"vertexai": True, "location": "global"},
    ),
    instruction=(
        "You are a Store Manager Assistant responsible for overall store "
        "operations. Your job:\n"
        "- Provide store information such as opening hours, contact details, "
        "and store policies using store tools.\n"
        "- For any inventory questions, listing SKUs, checking item stock, "
        "or updating item quantities, delegate to the inventory_assistant.\n\n"
        "Be conversational, helpful, and concise."
    ),
    tools=[get_store_info, AgentTool(inventory_remote_agent)],
)
