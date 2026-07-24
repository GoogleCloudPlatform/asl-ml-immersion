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
from typing import Literal

from google.adk import Agent
from google.adk import Event
from google.adk import Workflow
from pydantic import BaseModel
from pydantic import Field
from pydantic import BaseModel, Field
from google.adk import Event
from google.adk.events import RequestInput

MODEL = "gemini-2.5-flash"

# ==========================================
# 1. Schemas for Structured I/O
# ==========================================
class FlightInput(BaseModel):
    destination: str = Field(description="Destination city or airport code")
    departure_date: str = Field(description="Departure date (YYYY-MM-DD)")

class FlightResult(BaseModel):
    flight_number: str = Field(description="The booked flight number")
    price: float = Field(description="Total price of the booking")
    status: str = Field(description="Booking status (e.g., 'Confirmed')")

# ==========================================
# 2. Tool Definitions
# ==========================================
def get_weather(location: str) -> str:
    """Returns the current weather for a given location."""
    return f"The weather in {location} is 75°F and sunny."

def user_info() -> str:
    """Returns the user's home location."""
    return "User is located in SFO."

def geocode_address(address: str) -> str:
    """Gets coordinates for an address."""
    return "Lat: 37.7749, Lon: -122.4194"

def search_flights(destination: str, date: str) -> str:
    """Searches for available flights."""
    return f"Found flight UA123 to {destination} on {date} for $450."

def book_flight(flight_number: str) -> str:
    """Books the specified flight."""
    return f"Flight {flight_number} successfully booked!"

# ==========================================
# 3. Sub-Agents
# ==========================================
weather_agent = Agent(
    name="weather_checker",
    model=MODEL,
    mode="single_turn",         # Fire-and-forget: autonomous, no user interaction
    instruction="Check the weather for the requested destination using the provided tools. Report it back concisely.",
    tools=[get_weather, user_info, geocode_address],
)

flight_agent = Agent(
    name="flight_booker",
    model=MODEL,
    mode="task",                # Interactive: can ask the user clarifying questions
    instruction="Help the user search for and book a flight. You must confirm the details with the user before actually calling the booking tool.",
    input_schema=FlightInput,
    output_schema=FlightResult,
    tools=[search_flights, book_flight],
)

# ==========================================
# 4. Coordinator Agent (Root)
# ==========================================
root_agent = Agent(
    name="travel_planner",# Coordinator agent
    model=MODEL,      #
    instruction=(
        "You are a travel planning coordinator. Help users plan trips by delegating to your specialist agents:\n"
        "- Use `request_task_weather_checker` to check destination weather (autonomous, no user interaction needed).\n"
        "- Use `request_task_flight_booker` for flight search and booking (interactive, the user can discuss options).\n\n"
        "Start by checking the weather for their destination, then help them book the flight."
    ),
    sub_agents=[weather_agent, flight_agent],
    # The ADK automatically injects the tools: 
    # `request_task_weather_checker` and `request_task_flight_booker`
)