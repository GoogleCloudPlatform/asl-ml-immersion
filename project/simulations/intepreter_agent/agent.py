import asyncio
from unittest import result
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google import genai
from google.adk.tools import VertexAiSearchTool

## TODO: change to using .env values
# GCP Globals
PROJECT_ID = "qwiklabs-asl-00-58d3f08e551b"
REGION = "global"

# Generative Model to use
GENERATIVE_MODEL = "gemini-2.5-flash"

# Test Session/User Constants
SESSION_ID = "session_interpret_1"
USER_ID = "user_interpret_1"

# Function to call after agent completes
def post_search_logic(
    tool_response
):
    results = tool_response.get("results", []) if isinstance(tool_response, dict) else []

    wrapped_results = []
    for r in results:
        snippet = r.get("snippet")
        metadata = r.get("metadata", {})
        wrapped_results.append({
            "snippet": snippet,
            "source": metadata.get("source"),
            "document_id": metadata.get('document_id'),
            "score": metadata.get("score")
        })

    new_response = {
        "wrapped_results": wrapped_results,
        "original_response": tool_response
    }
    
    return new_response

# Agent Definition
root_agent = LlmAgent(
    # name, description available to other agents (Clear and descriptive metadata)
    name="interpreter_agent",
    description=f"Turns a list of LLM evaluation scores into one natural language summary for later evaluation",
    # Needs to be a gemini model, instruction is the system instruction for agent
    model=GENERATIVE_MODEL,
    instruction=f"""
        <PERSONA>
            You are The Interpreter: a clear, fair, and concise evaluator of model outputs.
            You translate structured evaluation metrics into natural-language feedback that a PM or researcher can read in under a minute.
            You are neutral, evidence-based, and specific. You never guess; you cite the metrics you see.
        </PERSONA>
        <INSTRUCTIONS>
            1. Collect the scores and reasoning for said scores together.
            2. Summarize the performance as reported by said scores and reasoning.
        <METRIC DESCRIPTIONS>
            The following is a brief description of the meaning of each scoring metric:
            {metric_descriptions}
        </METRIC DESCRIPTIONS>
        <RULES>
            1. Do not invent metrics; only discuss what’s present.
            2. Apply these thresholds: {scoring_thresholds}
            3. Handle contradictions by noting them and preferring the metric with explicit "reasoning".
        </RULES>
        <TONE>
            1. Answer should be clear and concise.
            2. Answer should be brief and easily understood, avoiding verbosity.
        </TONE>
    """,
    generate_content_config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)