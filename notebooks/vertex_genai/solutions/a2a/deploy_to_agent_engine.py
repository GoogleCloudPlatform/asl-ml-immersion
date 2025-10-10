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

import vertexai
from vertexai.preview import reasoning_engines
from vertexai import agent_engines
from dotenv import load_dotenv
import os
from purchasing_concierge.agent import root_agent

load_dotenv()

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
STAGING_BUCKET = os.getenv("STAGING_BUCKET")

vertexai.init(
    project=PROJECT_ID,
    location=LOCATION,
    staging_bucket=STAGING_BUCKET,
)

adk_app = reasoning_engines.AdkApp(
    agent=root_agent,
)

remote_app = agent_engines.create(
    agent_engine=adk_app,
    display_name="purchasing-concierge",
    requirements=[
        "google-cloud-aiplatform[agent_engines]",
        "google-adk==1.15.1",
        "a2a-sdk==0.2.16",
    ],
    extra_packages=[
        "./purchasing_concierge",
    ],
    env_vars={
        "GOOGLE_GENAI_USE_VERTEXAI": os.environ["GOOGLE_GENAI_USE_VERTEXAI"],
        "PIZZA_SELLER_AGENT_URL": os.environ["PIZZA_SELLER_AGENT_URL"],
        "BURGER_SELLER_AGENT_URL": os.environ["BURGER_SELLER_AGENT_URL"],
    },
)

print(f"Deployed remote app resource: {remote_app.resource_name}")
