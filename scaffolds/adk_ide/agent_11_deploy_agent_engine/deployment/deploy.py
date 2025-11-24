import vertexai
from vertexai.preview.reasoning_engines import AdkApp
from vertexai import agent_engines
from dotenv import load_dotenv
import os

from agent11_deploy_agent_engine.agent import root_agent

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

print("-" * 50)
print("Deploying app begin...")
app = AdkApp(
    agent=root_agent,
    enable_tracing=True,
)

AGENT_WHL_FILE = "./agent11_deploy_agent_engine-0.1.0-py3-none-any.whl"

print("Deploying agent to agent engine...")
remote_app = agent_engines.create(
    app,
    requirements=[
        AGENT_WHL_FILE,
    ],
    extra_packages=[
        AGENT_WHL_FILE,
    ],
)
print("Deploying agent to agent engine finished.")
print("-" * 50)

print("Testing deployemnt:")
session = remote_app.create_session(user_id="123")
for event in remote_app.stream_query(
    user_id="123",
    session_id=session["id"],
    message="Hello!",
):
    print(event)
print("Testing deployemnt finished!")
print("-" * 50)
