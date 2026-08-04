# reservation_agent/agent.py
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.tools import ToolContext

# App-scoped state prefix ensures reservations persist across all sessions.
# See https://adk.dev/sessions/state/ for state scope details.
STATE_PREFIX = "app:reservation:"


def create_reservation(
    phone_number: str,
    name: str,
    party_size: int,
    date: str,
    time: str,
    tool_context: ToolContext,
) -> dict:
    """Create a new restaurant reservation.

    Args:
        phone_number: Customer's phone number, used as the reservation ID.
        name: Name for the reservation.
        party_size: Number of guests.
        date: Reservation date (e.g., '2025-07-15' or 'this Friday').
        time: Reservation time (e.g., '7:00 PM').

    Returns:
        Confirmation of the reservation.
    """
    reservation = {
        "name": name,
        "party_size": party_size,
        "date": date,
        "time": time,
        "status": "confirmed",
    }
    tool_context.state[f"{STATE_PREFIX}{phone_number}"] = reservation
    return {
        "status": "confirmed",
        "message": f"Reservation created for {name}, party of {party_size} on {date} at {time}. Phone: {phone_number}.",
    }


def check_reservation(phone_number: str, tool_context: ToolContext) -> dict:
    """Look up an existing reservation by phone number.

    Args:
        phone_number: The phone number used when the reservation was created.
        tool_context: ADK tool context for state access.

    Returns:
        The reservation details, or a message if not found.
    """
    reservation = tool_context.state.get(f"{STATE_PREFIX}{phone_number}")
    if reservation:
        return {"found": True, "reservation": reservation}
    return {"found": False, "message": f"No reservation found for {phone_number}."}


def cancel_reservation(phone_number: str, tool_context: ToolContext) -> dict:
    """Cancel an existing reservation by phone number.

    Args:
        phone_number: The phone number used when the reservation was created.
        tool_context: ADK tool context for state access.

    Returns:
        Confirmation of cancellation, or a message if not found.
    """
    key = f"{STATE_PREFIX}{phone_number}"
    reservation = tool_context.state.get(key)
    if not reservation:
        return {
            "success": False,
            "message": f"No reservation found for {phone_number}.",
        }
    if reservation.get("status") == "cancelled":
        return {
            "success": False,
            "message": f"Reservation for {phone_number} is already cancelled.",
        }
    reservation["status"] = "cancelled"
    tool_context.state[key] = reservation
    return {
        "success": True,
        "message": f"Reservation for {reservation['name']} ({phone_number}) has been cancelled.",
    }


root_agent = LlmAgent(
    name="reservation_agent",
    description="Handles restaurant table reservations — create, check, and cancel bookings for Foodie Finds restaurant.",
    model=Gemini(
        model="gemini-3.5-flash",
        client_kwargs={"vertexai": True, "location": "global"},
    ),
    instruction="""You are a friendly reservation assistant for "Foodie Finds" restaurant.
You help diners create, check, and cancel table reservations.

When a diner wants to make a reservation, collect these details:
- Name for the reservation
- Phone number (used as the reservation ID)
- Party size (number of guests)
- Date
- Time

When all required reservation details are provided, immediately execute the create_reservation tool without asking for extra confirmation.
When checking or cancelling, ask for the phone number if not provided.
Be concise and professional.""",
    tools=[create_reservation, check_reservation, cancel_reservation],
)
