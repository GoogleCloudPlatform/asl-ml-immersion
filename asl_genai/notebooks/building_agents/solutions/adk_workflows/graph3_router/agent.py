"""ADK 2.x Routing Workflow."""

from google.adk import Agent, Event, Workflow

MODEL = "gemini-2.5-flash"

# 1. LLM Classifier Agent
process_message = Agent(
    name="process_message",
    model=MODEL,
    instruction="""Classify user message into either "BUG", "CUSTOMER_SUPPORT",
     or "LOGISTICS". If you think a message applies to more than one category,
     reply with a comma separated list of categories.
  """,
    output_schema=str,
)


# 2. Router Node
def router(node_input: str):
    # Split the comma-separated string from the LLM
    routes = node_input.split(",")
    # Clean up any whitespace
    routes = [route.strip() for route in routes]

    # Emitting an Event with 'route' dictates the next edge(s) to traverse
    return Event(route=routes)


# 3. Destination Nodes
def response_1_bug():
    return Event(message="Handling bug...")


def response_2_support():
    return Event(message="Handling customer support...")


def response_3_logistics():
    return Event(message="Handling logistics...")


# 4. Construct Workflow
root_agent = Workflow(
    name="routing_workflow",
    edges=[
        # 1. Start execution at the LLM classifier, then pass output to router
        ("START", process_message, router),
        # 2. Map the routes emitted by the router to the destination nodes
        (
            router,
            {
                "BUG": response_1_bug,
                "CUSTOMER_SUPPORT": response_2_support,
                "LOGISTICS": response_3_logistics,
            },
        ),
    ],
)
