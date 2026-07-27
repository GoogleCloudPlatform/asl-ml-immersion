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

#from .tools import get_weather

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "New York", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(
        f"--- Tool: get_weather called for city: {city} ---"
    )  # Log tool execution
    city_normalized = city.lower().replace(" ", "")  # Basic normalization

    # Mock weather data
    mock_weather_db = {
        "newyork": {
            "status": "success",
            "report": """
            The weather in New York is sunny with a temperature of 25°C.
            """,
        },
        "london": {
            "status": "success",
            "report": """
            It's cloudy in London with a temperature of 15°C.
            """,
        },
        "tokyo": {
            "status": "success",
            "report": """
            Tokyo is experiencing light rain and a temperature of 18°C.
            """,
        },
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {
            "status": "error",
            "error_message": f"""
            Sorry, I don't have weather information for '{city}'.
            """,
        }


root_agent = Agent(
    name="weather_agent_v1",
    model=MODEL,  # Can be a string for Gemini or a LiteLlm object
    description="Provides weather information for specific cities.",
    instruction="You are a helpful weather assistant. "
    "When the user asks for the weather in a specific city, "
    "use the 'get_weather' tool to find the information. "
    "If the tool returns an error, inform the user politely. "
    "If the tool is successful, present the weather report clearly.",
    tools=[get_weather],  # Pass the function directly
)

import os
import vertexai
from dotenv import load_dotenv
from vertexai.agent_engines import AdkApp
import agentplatform

load_dotenv()

cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
storage_bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")

print(f"cloud_project={cloud_project}")
print(f"cloud_location={cloud_location}")
print(f"storage_bucket={storage_bucket}")

BUCKET_URI = f"gs://{storage_bucket}"

print("-" * 50)
print("Deploying app begin...")

adk_app = AdkApp(agent=root_agent)

print("Deploying agent to agent engine...")

DISPLAY_NAME = root_agent.name
env_vars = {
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true",
    "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true",
}

client = agentplatform.Client(project=cloud_project, location=cloud_location)

remote_app = client.agent_engines.create(
    agent=adk_app,
    config={
        "display_name": DISPLAY_NAME,
        "description": "Weather Agent TEST",
        "requirements": [
            "google-adk==2.5.0",
            "google-genai==2.11.0",
            "google-cloud-aiplatform[agent_engines,adk]",
            "cloudpickle",
            "pydantic",
        ],
        "env_vars": env_vars,
        "staging_bucket": BUCKET_URI,
    },
)
print("Deploying agent to agent engine finished.") 
print(f"Created remote agent: {remote_app.api_resource.display_name}")
print("-" * 50)