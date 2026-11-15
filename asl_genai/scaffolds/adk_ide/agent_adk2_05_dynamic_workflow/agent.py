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
from google.adk import Context
from google.adk import Workflow
from google.adk.workflow import node
from typing import Any

MODEL = "gemini-2.5-flash"

@node(name="hello_node")
def my_node(node_input: Any):
    return "Hello World"

# define a dynamic workflow node
@node(rerun_on_resume=True)
async def my_workflow(ctx: Context, node_input: str) -> str:
    # run_node executes a node and returns its output
    result = await ctx.run_node(my_node, node_input=node_input)
    return result

# Run the workflow
root_agent = Workflow(
    name="root_agent",
    edges=[("START", my_workflow)],
)
