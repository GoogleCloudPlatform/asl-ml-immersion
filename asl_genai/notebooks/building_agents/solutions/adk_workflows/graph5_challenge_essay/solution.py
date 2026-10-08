"""ADK 2.x Essay Writing Agentic Workflow (Solution)."""

from typing import Literal

from google.adk import Agent, Event, Workflow
from google.adk.tools import google_search
from pydantic import BaseModel, Field

MODEL = "gemini-3.8-flash"
MAX_REVISIONS = 2


# =====================================================================
# 1. Structured Evaluation Schema
# =====================================================================
class CritiqueFeedback(BaseModel):
    grade: Literal["accept", "revise"] = Field(
        description=(
            "Decide if the essay is thorough, well-structured, and meets high "
            "standards ('accept'), or if it needs improvement ('revise')."
        ),
    )
    critique: str = Field(
        description=(
            "Detailed recommendations and critique on how to improve the essay "
            "if revised, or commendations if accepted."
        ),
    )


# =====================================================================
# 2. Input Processing Node
# =====================================================================
def process_input(node_input: str):
    """Stores initial essay topic in state."""
    return Event(state={"topic": node_input})


# =====================================================================
# 3. Specialist Agents
# =====================================================================
planner_agent = Agent(
    name="planner_agent",
    model=MODEL,
    instruction="""
    You are an expert writer tasked with writing a high-level outline of an essay.
    Write an outline for the user provided topic: "{topic}".
    Use Google Search to research the topic and provide a clear outline along with key arguments and notes for each section.
    """,
    tools=[google_search],
    output_key="plan",
)

writer_agent = Agent(
    name="writer_agent",
    model=MODEL,
    instruction="""
    You are an essay writer tasked with writing an excellent essay.
    Generate the best essay possible based on the outline:
    ---
    Plan:
    {plan}
    ---
    If critique is provided below, respond with a revised version of your previous draft:
    {critique?}

    Use Markdown formatting to specify a title and section headers for each paragraph.
    """,
    tools=[google_search],
    output_key="draft",
)

evaluator_agent = Agent(
    name="evaluator_agent",
    model=MODEL,
    instruction="""
    You are an exacting academic professor grading an essay submission.
    Hold initial drafts to rigorous scholarly standards.

    Read the essay draft below and evaluate whether it meets academic publication standards:
    ---
    {draft}
    ---

    Evaluation criteria:
    1. Initial Submission Rigor: First drafts must be critically evaluated. Unless the draft demonstrates that it has already incorporated prior critical feedback and includes specific real-world case studies or empirical evidence, challenge the author to improve.
    2. Evidence & Case Studies: Demand concrete real-world case studies, specific named examples, or empirical statistics (not vague generalizations).
    3. Counter-arguments: The essay must address opposing viewpoints and ethical dilemmas with depth.

    Grading rule:
    - If the draft lacks concrete named case studies/evidence, or has not yet undergone revision to address critical feedback, assign grade 'revise' with demanding, actionable recommendations on what to expand.
    - If the draft is thorough, incorporates specific real-world examples/case studies, and addresses counter-arguments well, assign grade 'accept'.
    """,
    output_schema=CritiqueFeedback,
    output_key="critique_result",
)


# =====================================================================
# 4. Router and Finalizer Nodes
# =====================================================================
def route_critique(node_input: CritiqueFeedback, revision_count: int = 0):
    """Routes back to writer if revisions are needed."""
    if node_input.grade == "revise" and revision_count < MAX_REVISIONS:
        return Event(
            state={
                "critique": node_input.critique,
                "revision_count": revision_count + 1,
            },
            route="revise",
        )
    return Event(state={"critique": node_input.critique}, route="accept")


def finalize_essay(draft: str):
    """Displays the final accepted essay."""
    return Event(
        message=(
            f"### Final Essay\n\n{draft}\n\n---\n*Essay refinement complete.*"
        )
    )


# =====================================================================
# 5. Construct Workflow Graph
# =====================================================================
root_agent = Workflow(
    name="essay_writing_workflow",
    edges=[
        (
            "START",
            process_input,
            planner_agent,
            writer_agent,
            evaluator_agent,
            route_critique,
        ),
        (
            route_critique,
            {
                "revise": writer_agent,
                "accept": finalize_essay,
            },
        ),
    ],
)
