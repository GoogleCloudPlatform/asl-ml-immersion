"""ADK 2.x Human-in-the-Loop Workflow."""

from google.adk import Agent, Event, Workflow
from google.adk.events import RequestInput

MODEL = "gemini-2.5-flash"


def process_input(node_input: str):
    """Takes initial customer complaint as input and sets state."""
    return Event(state={"complaint": node_input, "feedback": ""})


draft_email = Agent(
    name="draft_email",
    model=MODEL,
    instruction="""
    Please write a polite, helpful response email to customer complaint:
    "{complaint}"
    If there is feedback from the manager to revise draft, incorporate it:
    "{feedback?}"
    """,
    output_key="draft",
)


def request_human_review(draft: str):
    return RequestInput(
        message=(
            "Please review the following draft email and provide "
            f"'approve', 'reject', or feedback to revise.\n\n---\n{draft}\n---"
        )
    )


def handle_human_review(node_input: str):
    user_resp = node_input.lower().strip()
    if user_resp == "reject":
        return Event(route="rejected")
    if user_resp == "approve":
        return Event(route="approved")
    return Event(state={"feedback": node_input}, route="revise")


def reject_email():
    return Event(message="Draft rejected.")


def send_email(draft: str):
    # pylint: disable=unused-argument
    return Event(message="Draft approved and sent successfully.")


root_agent = Workflow(
    name="hitl_workflow",
    edges=[
        (
            "START",
            process_input,
            draft_email,
            request_human_review,
            handle_human_review,
        ),
        (
            handle_human_review,
            {
                "revise": draft_email,
                "approved": send_email,
                "rejected": reject_email,
            },
        ),
    ],
)
