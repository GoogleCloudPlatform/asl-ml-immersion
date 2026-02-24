"""
Deploys the agent to the Vertex AI Agent Engine.
"""

import os

import vertexai
from agent_01_tool_func.agent import root_agent
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview.reasoning_engines import AdkApp

load_dotenv()

cloud_project = os.getenv("GOOGLE_CLOUD_PROJECT")
cloud_location = os.getenv("GOOGLE_CLOUD_LOCATION")
storage_bucket = os.getenv("GOOGLE_CLOUD_STORAGE_BUCKET")


print(f"cloud_project={cloud_project}")
print(f"cloud_location={cloud_location}")
print(f"storage_bucket={storage_bucket}")

vertexai.init(
    project=cloud_project,
    location=cloud_location,
    staging_bucket=f"gs://{storage_bucket}",
)

def deploy_agent():
    print("-" * 50)
    print("Deploying app begin...")
    adk_app = AdkApp(
        agent=root_agent,
        enable_tracing=True,
    )

    DISPLAY_NAME = root_agent.name

    print("Deploying agent to agent engine...")
    remote_app = agent_engines.create(
        adk_app,
        display_name=DISPLAY_NAME,
        description="Weather Agent v22",
        requirements=[
            "google-adk (==1.21.0)",
            #"google-adk[a2a,eval,extensions,otel-gcp]==1.21.0",
        ],
        #extra_packages=["./agent_01_tool_func"],
    )
    print("Deploying agent to agent engine finished.")
    print("-" * 50)
    print(f"Created remote agent: {remote_app.resource_name}")
    print("Testing agent...")
    session = remote_app.create_session(user_id="123")
    for event in remote_app.stream_query(
        user_id="123",
        session_id=session["id"],
        message="Hello!",
    ):
        print(event)
    print("Testing agent finished!")
    print("-" * 50)


if __name__ == "__main__":
    deploy_agent()
