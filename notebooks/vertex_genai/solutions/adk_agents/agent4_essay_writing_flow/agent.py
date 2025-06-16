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
First, based on the topic and outline from the user,
create search queries, run the search tool to get information, and collect the information.
Next, generate the best essay possible using the initial request, the outline, and the research provided.
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

search_agent = LlmAgent(
    name="basic_search_agent",
    model=MODEL,
    description="Agent to answer questions using Google Search.",
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    # google_search is a pre-built tool which allows the agent to perform Google searches.
    tools=[google_search],
)


# Agent to write the essay, using context from the conversation
initial_writer_agent = LlmAgent(
    name="initial_writer_agent",
    model=MODEL,
    instruction=INITIAL_WRITER_PROMPT,
    tools=[AgentTool(search_agent)],
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
    tools=[AgentTool(search_agent)],
    output_key="draft",
)

# The loop for refining the essay: Reflect -> Research Critique -> Rewrite
refinement_loop = LoopAgent(
    name="refinement_loop",
    sub_agents=[reflection_agent, writer_agent],
    max_iterations=3,
)

# The main sequential agent that orchestrates the entire process
essay_writing_agent = SequentialAgent(
    name="essay_writing_agent",
    sub_agents=[
        planner_agent,
        # research_agent,
        initial_writer_agent,
        refinement_loop,
    ],
)

root_agent = essay_writing_agent
