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
from google.adk.code_executors import VertexAiCodeExecutor
import os

MODEL = "gemini-2.5-flash"

# You can optionally provide a resource_name for an existing Code Interpreter Extension instance
# VERTEX_CODE_EXECUTOR_ID="projects/9...4/locations/us-central1/extensions/7...2"
VERTEX_CODE_EXECUTOR_ID=None

# Will create or use an existing one VertexAiCodeExecutor based on env var or default
try:
    if VERTEX_CODE_EXECUTOR_ID:
        print("Initializing VertexAiCodeExecutor...")
        vertex_executor = VertexAiCodeExecutor(resource_name=VERTEX_CODE_EXECUTOR_ID)
    else:
        print("Creating new VertexAiCodeExecutor...")
        vertex_executor = VertexAiCodeExecutor()
        print(f"VertexAiCodeExecutor initialized: {vertex_executor._code_interpreter_extension.gca_resource.name}")

except Exception as e:
    print(f"Failed to initialize VertexAiCodeExecutor. Ensure Vertex AI API is enabled")

root_agent = Agent(
    name="vertex_code_agent",
    model=MODEL,
    instruction="""You are an programming advanced AI assistant. 
        Write Python code to perform calculations or data tasks. 
        Your code will be executed in a secure Vertex AI environment. 
        Default libraries like pandas, numpy, matplotlib are available.""",
    code_executor=vertex_executor
)