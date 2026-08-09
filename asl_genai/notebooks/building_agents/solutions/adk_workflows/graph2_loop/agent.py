"""ADK 2.x Evaluator-Optimizer Refinement Loop Workflow."""

from typing import Literal

from google.adk import Agent, Event, Workflow
from pydantic import BaseModel, Field

MODEL = "gemini-2.5-flash"


class Feedback(BaseModel):
    grade: Literal["tech-related", "unrelated"] = Field(
        description=(
            "Decide if the headline is related to technology or software "
            "engineering."
        ),
    )
    feedback: str = Field(
        description=(
            "If the headline is unrelated to technology, provide feedback "
            "on how to make it more tech-focused."
        ),
    )


def process_input(node_input: str):
    """Puts user input in the state."""
    return Event(state={"topic": node_input})


generate_headline = Agent(
    name="generate_headline",
    model=MODEL,
    instruction="""
    Write a headline about the topic "{topic}".
    If feedback is provided, take it into account.
    The feedback: {feedback?}
    """,
)

evaluate_headline = Agent(
    name="evaluate_headline",
    model=MODEL,
    instruction="""
    Grade whether the headline is related to technology or software engineering.
    """,
    output_schema=Feedback,
    output_key="feedback",
)


def route_headline(node_input: Feedback):
    return Event(route=node_input.grade)


root_agent = Workflow(
    name="evaluator_optimizer_loop",
    edges=[
        (
            "START",
            process_input,
            generate_headline,
            evaluate_headline,
            route_headline,
        ),
        # The Refinement Loop:
        (route_headline, {"unrelated": generate_headline}),
    ],
)
