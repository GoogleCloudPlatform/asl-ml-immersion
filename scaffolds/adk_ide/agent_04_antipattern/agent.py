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
from google.adk.agents import Agent

MODEL = "gemini-2.5-flash"

"""god_agent.py - The monolithic 'God Agent' anti-pattern."""

def get_weather(city: str) -> dict:
    """Retrieves current weather status and wind speed for a specific city.
    
    Args:
        city: The name of the city.
    """
    # Simulate a severe weather condition for testing
    if city.lower() == "miami":
        return {"city": "Miami", "wind_speed": 65, "status": "Severe Storm"}
    return {"city": city, "wind_speed": 12, "status": "Sunny"}


def send_alert_email(recipient: str, subject: str, body: str) -> str:
    """Sends a critical weather alert email to a subscriber.
    
    Args:
        recipient: Email address of the recipient.
        subject: Email subject.
        body: Body of the email.
    """
    print(f"[Email Tool] Alert sent to {recipient}: {subject}")
    return "SUCCESS"


def log_incident_in_crm(system: str, details: str) -> str:
    """Logs a system incident or execution failure in the CRM database.
    
    Args:
        system: The sub-system affected.
        details: Error message or detail logs.
    """
    print(f"[CRM Tool] Incident logged for {system}: {details}")
    return "INCIDENT_LOGGED"


# --- THE "GOD AGENT" ANTI-PATTERN ---
# A single agent attempting to orchestrate an entire operational workflow.
# Operational rules, state transitions, human-in-the-loop approvals, 
# and error handling are all hidden inside unstructured natural language.
root_agent = Agent(
    name="weather_agent",
    model=MODEL,
    description="Monolithic manager that handles weather queries, alerts, and logging.",
    instruction=(
        "You are an automated disaster-response coordinator. Carefully execute these steps in order:\n\n"
        "1. CLASSIFY: First, check if the request is about weather or a system error.\n"
        "2. RETRIEVE: If it is about weather, call the 'get_weather' tool.\n"
        "3. EVALUATE RISK: Check the wind speed and status returned. If wind speed is over 50mph "
        "or if there is a 'Severe Storm' status, this is considered HIGH RISK.\n"
        "4. ASK APPROVAL: If the risk is HIGH RISK, you MUST ask the user for explicit permission "
        "('Should I send the email alert?') and wait for confirmation before doing anything else. "
        "DO NOT call the 'send_alert_email' tool without this confirmation.\n"
        "5. ACT: If risk is LOW RISK, immediately call the 'send_alert_email' tool without asking.\n"
        "6. RETRY POLICY: If 'get_weather' fails, retry it up to 2 times. If 'send_alert_email' fails, "
        "DO NOT retry it under any circumstances, to prevent spamming the recipient.\n"
        "7. LOG: If any critical tool failure occurs, log the incident using the 'log_incident_in_crm' tool."
    ),
    tools=[get_weather, send_alert_email, log_incident_in_crm],
)

