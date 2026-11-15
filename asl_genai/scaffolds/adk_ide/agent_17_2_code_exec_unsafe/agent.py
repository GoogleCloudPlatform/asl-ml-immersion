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
from google.adk.code_executors import UnsafeLocalCodeExecutor

import os

MODEL = "gemini-2.5-flash"

root_agent = Agent(
    name="adk_code_agent",
    model=MODEL,
    instruction="""You are a helpful assistant that can write and execute
        Python code to answer questions, especially for calculations or data analysis.
        When you write code, it will be automatically executed.""",
    code_executor=UnsafeLocalCodeExecutor()
)