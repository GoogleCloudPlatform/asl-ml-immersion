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
from google.adk import Agent, Workflow

MODEL = "gemini-2.5-flash"

# ==========================================
# 1. CORE TOOLS & ERROR POLICIES
# ==========================================

def get_weather(city: str) -> dict:
    """Retrieves current weather status and wind speed for a specific city.
    
    Includes deterministic retries (up to 2 times on error).
    """
    retries = 2
    for attempt in range(retries + 1):
        try:
            if city.lower() == "miami":
                return {"city": "Miami", "wind_speed": 65, "status": "Severe Storm"}
            return {"city": city, "wind_speed": 12, "status": "Sunny"}
        except Exception as e:
            if attempt == retries:
                raise RuntimeError(f"get_weather failed after {retries} retries: {e}")

def send_alert_email(recipient: str, subject: str, body: str) -> str:
    """Sends a critical weather alert email to a subscriber.
    
    No-retry policy: If this fails, standard exceptions propagate to trigger logging.
    """
    print(f"[Email Tool] Alert sent to {recipient}: {subject}")
    return "SUCCESS"

def log_incident_in_crm(system: str, details: str) -> str:
    """Logs a system incident or execution failure in the CRM database."""
    print(f"[CRM Tool] Incident logged for {system}: {details}")
    return "INCIDENT_LOGGED"


# ==========================================
# 2. SPECIALIZED WORKER AGENTS (AI NODES)
# ==========================================

approval_agent = Agent(
    name="approval_agent",
    model=MODEL,
    description="Asks the user for explicit permission to send weather alerts.",
    instruction=(
        "Ask the user for explicit permission to send the weather alert "
        "(e.g., 'Should I send the email alert?'). Wait for their input. "
        "Do NOT call the send_alert_email tool yourself."
    )
)

email_alerter = Agent(
    name="email_alerter",
    model=MODEL,
    description="Sends the critical weather alert email to the recipient.",
    instruction="Call the 'send_alert_email' tool to dispatch the weather alert. Ensure you only send it once.",
    tools=[send_alert_email]
)

crm_logger = Agent(
    name="crm_logger",
    model=MODEL,
    description="Logs critical workflow errors in the CRM.",
    instruction="Call the 'log_incident_in_crm' tool to log errors, precisely detailing which sub-system failed.",
    tools=[log_incident_in_crm]
)


# ==========================================
# 3. DETERMINISTIC ROUTERS (PURE CODE NODES)
# ==========================================

def evaluate_risk(weather_data: dict) -> str:
    """Deterministically classifies weather risk based on tool output."""
    wind_speed = weather_data.get("wind_speed", 0)
    status = weather_data.get("status", "")
    
    if wind_speed > 50 or status.lower() == "severe storm":
        return "HIGH_RISK"
    return "LOW_RISK"

def evaluate_approval(user_response: str) -> str:
    """Deterministically evaluates the user's approval response."""
    response = user_response.lower()
    if any(keyword in response for keyword in ["yes", "approve", "confirm", "send", "should"]):
        return "APPROVED"
    return "DENIED"

def skip_alert(input_data: str) -> str:
    """Terminal node used when approval is denied."""
    print("[Workflow] Alert was denied. Exiting without sending email.")
    return "WORKFLOW_TERMINATED_NO_SEND"


# ==========================================
# 4. THE WORKFLOW GRAPH
# ==========================================

root_agent = Workflow(
    name="disaster_response_workflow",
    edges=[
        # Step 1: Start at get_weather node (Input city is passed dynamically) [16]
        ("START", get_weather),
        
        # Step 2: Pass weather data straight into the deterministic evaluation router
        (get_weather, evaluate_risk),
        
        # Step 3: Branch conditionally based on risk classification
        (evaluate_risk,
          {
              "HIGH_RISK": approval_agent,
              "LOW_RISK": email_alerter,
          }
        )
        
        # Step 4: If HIGH_RISK, routing depends on the user response analyzed by approval evaluator
        (approval_agent, evaluate_approval),

        (evaluate_approval,
          {
              "APPROVED": email_alerter,
              "DENIED": skip_alert,
          }
        )
    ]
)
