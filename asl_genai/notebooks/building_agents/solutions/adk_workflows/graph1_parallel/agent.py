"""ADK 2.x Parallel Processing Workflow."""

# pylint: disable=invalid-name

from google.adk import Event, Workflow
from google.adk.workflow import JoinNode


# 1. Define Parallel Processing Nodes (A, B, C)
def node_A(node_input: str):
    return Event(
        message=f"Node A executed... input={node_input}",
        output=int(node_input),
    )


def node_B(node_input: str):
    input_b = int(node_input)
    return Event(
        message=f"Node B executed... input={node_input}",
        output=input_b * 100,
    )


def node_C(node_input: str):
    input_c = int(node_input)
    return Event(
        message=f"Node C executed... input={node_input}",
        output=input_c * input_c,
    )


# 2. Define Aggregation and Display Node (D)
def node_D(node_input: dict) -> Event:
    """Collects outputs from JoinNode, calculates the sum, and displays it."""
    val_a = node_input.get("node_A", 0.0)
    val_b = node_input.get("node_B", 0.0)
    val_c = node_input.get("node_C", 0.0)

    total_sum = val_a + val_b + val_c

    display_message = (
        f"### Execution Complete!\n\n"
        f"Successfully collected parallel outputs:\n"
        f"- **Node A Output:** `{val_a}`\n"
        f"- **Node B Output:** `{val_b}`\n"
        f"- **Node C Output:** `{val_c}`\n\n"
        f"---\n"
        f"### Result\n"
        f"**Node D (Total Sum):** `{total_sum}`"
    )

    return Event(message=display_message, output=total_sum)


join_node = JoinNode(name="join_node")

# 3. Construct Workflow
root_agent = Workflow(
    name="parallel_workflow",
    edges=[
        ("START", node_A, join_node),
        ("START", node_B, join_node),
        ("START", node_C, join_node),
        (join_node, node_D),
    ],
)
