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

from google.adk import Agent
from google.adk import Workflow
from google.adk import Event
from google.adk.workflow import JoinNode
from google.genai.types import Content, Part

def node_A(node_input: str):
    return Event(
        message=f"Node A executed... input={node_input}", 
        output=int(node_input)
    )

def node_B(node_input: str):
    input_b = int(node_input)
    return Event(
        message=f"Node B executed... input={node_input}", 
        output=input_b * 100
    )

def node_C(node_input: str):
    input_c = int(node_input)
    return Event(
        message=f"Node C executed... input={node_input}", 
        output=input_c * input_c
    )

# ==========================================
# 2. DEFINE AGGREGATION & DISPLAY NODE (D)
# ==========================================
def node_D(node_input: dict) -> Event:
    """
    Collects outputs from JoinNode, calculates the sum, and displays it.
    """
    # Safely extract outputs with a fallback of 0.0
    val_a = node_input.get("node_A", 0.0)
    val_b = node_input.get("node_B", 0.0)
    val_c = node_input.get("node_C", 0.0)

    # Calculate the sum
    total_sum = val_a + val_b + val_c

    # Format a clean markdown message to show to the user
    display_message = (
        f"### Execution Complete!\n\n"
        f"Successfully collected parallel outputs:\n"
        f"- Node A Output: `{val_a}`\n"
        f"- Node B Output: `{val_b}`\n"
        f"- Node C Output: `{val_c}`\n\n"
        f"--- \n"
        f"### Result\n"
        f"Node D (Total Sum): `{total_sum}`"
    )

    # Returning an Event with a 'message' displays it to the user in the UI
    return Event(message=display_message, output=total_sum)

join_node = JoinNode(name="join_node")

# Define the workflow topology
root_agent = Workflow(
    name="routing_workflow",
    edges=[
        ("START", node_A, join_node),
        ("START", node_B, join_node),
        ("START", node_C, join_node),
        (join_node, node_D),
    ],
)