# pylint: skip-file

import os

import google.adk as adk
from google.adk.agents import LlmAgent, LoopAgent, SequentialAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

MODEL = "gemini-2.5-flash"

# --- Agent Prompts ---

PLAN_PROMPT = """You are an expert writer tasked with writing a high level outline of an hands-on workshop.
Write such an outline for the user provided topic. Give an outline of the hands-on workshop along with any
relevant notes or instructions for the sections."""


INITIAL_WRITER_PROMPT = """
You are a tutorial write tasked with writing excellent 3-pages hands-on tutorial for hands-on workshop.
Generate the best tutorial possible using google search, based on the high level outline.
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

REFLECTION_PROMPT = """You are an experienced PyCon conference reviewer and workshop planning expert.
    Read the workshop proposal or outline provided by the user and generate constructive critique
    and actionable recommendations for it. Provide detailed feedback on the workshop's structure,
    clarity of learning objectives, proposed hands-on exercises, target audience fit,
    and estimated pacing to ensure it meets PyCon's standards for a high-quality, 
    engaging developer workshop."""


# --- Agent Definitions ---

# Agent to plan the workshop
workshop_plan_agent = LlmAgent(
    name="workshop_plan_agent",
    model=MODEL,
    instruction=PLAN_PROMPT,
    output_key="plan",
)

# Agent to write the workshop tutorial, using context from the conversation
initial_writer_agent = LlmAgent(
    name="initial_writer_agent",
    model=MODEL,
    instruction=INITIAL_WRITER_PROMPT,
    tools=[google_search],
    output_key="draft",
)

# Agent to critique the workshop tutorial
reflection_agent = LlmAgent(
    name="reflection_agent",
    model=MODEL,
    instruction=REFLECTION_PROMPT,
    output_key="critique",
)


# Agent to write the workshop tutorial, using context from the conversation
writer_agent = LlmAgent(
    name="writer_agent",
    model=MODEL,
    instruction=WRITER_PROMPT,
    tools=[google_search],
    output_key="draft",
)

# The loop for refining the workshop tutorial: Reflect -> Research Critique -> Rewrite
refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[reflection_agent, writer_agent],
    max_iterations=2,
)

# The main sequential agent that orchestrates the entire process
essay_writing_agent = SequentialAgent(
    name="essay_writing_agent",
    sub_agents=[
        workshop_plan_agent,
        initial_writer_agent,
        refinement_loop,
    ],
)

root_agent = essay_writing_agent
