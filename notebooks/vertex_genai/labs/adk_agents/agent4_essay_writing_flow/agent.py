# pylint: skip-file

import os

import google.adk as adk
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-2.0-flash"

# --- Agent Prompts ---

PLAN_PROMPT = """You are an expert writer tasked with writing a high level outline of an essay.
Write such an outline for the user provided topic. Give an outline of the essay along with any
relevant notes or instructions for the sections."""


INITIAL_WRITER_PROMPT = """
You are a essay write tasked with writing excellent 3-pages essays.
Generate the best essay possible using google search, based on the outline.
If critique is provided below, respond with a revised version of your previous attempts.
Use Markdown formatting to specify a title and section headers for each paragraph.
Utilize all of the information below as needed:
---
Plan:
{plan}

"""


WRITER_PROMPT = (
    INITIAL_WRITER_PROMPT
    + """
Critique:
{critique}
"""
)

REFLECTION_PROMPT = """You are a professor grading an essay submission.
Read the essay provided by the user and generate critique and recommendations for it.
Provide detailed recommendations about the essay."""


# --- Agent Definitions ---

# Agent to plan the essay outline
planner_agent = LlmAgent(
    name="planner_agent",
    model=MODEL,
    instruction=PLAN_PROMPT,
    output_key="plan",
)

# Agent to write the essay, using context from the conversation
initial_writer_agent = LlmAgent(
    name="initial_writer_agent",
    model=MODEL,
    instruction=INITIAL_WRITER_PROMPT,
    tools=[google_search],
    output_key="draft",
)

# Agent to critique the essay
reflection_agent = LlmAgent(
    name="reflection_agent",
    model=MODEL,
    instruction=REFLECTION_PROMPT,
    output_key="critique",
)


# Agent to write the essay, using context from the conversation
writer_agent = LlmAgent(
    name="writer_agent",
    model=MODEL,
    instruction=WRITER_PROMPT,
    tools=[google_search],
    output_key="draft",
)

# The loop for refining the essay: Reflect -> Research Critique -> Rewrite
refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[],  # TODO: Define the loop.
    max_iterations=2,
)

# The main sequential agent that orchestrates the entire process
essay_writing_agent = SequentialAgent(
    name="essay_writing_agent", sub_agents=[]  # TODO: Define a sequential flow.
)

root_agent = essay_writing_agent
