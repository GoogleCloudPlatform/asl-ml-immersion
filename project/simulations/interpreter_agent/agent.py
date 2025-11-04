import asyncio
from unittest import result
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google import genai
from google.adk.tools import VertexAiSearchTool
import time, uuid
from pydantic import BaseModel, Field

INTERPRETER_APP_NAME = "interpreter_app"

## TODO: change to using .env values
# GCP Globals
PROJECT_ID = "qwiklabs-asl-00-58d3f08e551b"
REGION = "global"

# Generative Model to use
GENERATIVE_MODEL = "gemini-2.5-flash"

async def create_session(user_id: str, session_id: str, session_service: InMemorySessionService):
    return await session_service.create_session(
        app_name=INTERPRETER_APP_NAME, 
        user_id=user_id, 
        session_id=session_id
    )

class InterpreterOuput(BaseModel):
    status: str = Field(description="The status of the interpretation.")
    interpretation: str = Field(description="The natural language interpreation of the evaluation metrics.")

def instantiate_interpreter_agent(parameters={}):
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
                {parameters['metric_descriptions']}
            </METRIC DESCRIPTIONS>
            <RULES>
                1. Do not invent metrics; only discuss what’s present.
                2. Apply these thresholds: {parameters['scoring_thresholds']}
                3. Handle contradictions by noting them and preferring the metric with explicit "reasoning".
            </RULES>
            <TONE>
                1. Answer should be clear and concise.
                2. Answer should be brief and easily understood, avoiding verbosity.
            </TONE>

            <QUESTION>
        """,
        generate_content_config=types.GenerateContentConfig(
            response_mime_type="application/json"
        ),
        output_schema=InterpreterOuput,
        ## can't transfer to parent or peers with output_schema defined
        disallow_transfer_to_parent = True,
        disallow_transfer_to_peers = True
    )

    session_service_interpreter_agent = InMemorySessionService()
    runner_interpreter_agent = Runner(
        agent=root_agent,
        app_name=INTERPRETER_APP_NAME,
        session_service=session_service_interpreter_agent
    )

    return session_service_interpreter_agent, runner_interpreter_agent

async def call_interpreter_agent(question, user_id="user_vsearch_1", session_id=None, parameters={}):
    print(f"\n--- Running Interpreter Agent ---")
    #print(f"User Question: <{question}>")
    #print(parameters)
    session_service, runner = instantiate_interpreter_agent(parameters)

    start_time = time.perf_counter()

    if not session_id:
        session_creation_start = time.perf_counter()
        session_id = str(uuid.uuid4())
        session = await create_session(user_id=user_id, session_id=session_id, session_service=session_service)
        session_id = session.id
        user_id = session.user_id
        session_creation_end = time.perf_counter()
        print(f"Created session <{session_id}> in <{session_creation_end-session_creation_start}> seconds.")


    content = types.Content(role='user', parts=[types.Part(text=question)])

    agent_response = {
        'question': question,
        'answer': 'No answer generated',
    }
    agent_response['answer'] = "No answer generated"

    
    try:
        start_time = time.perf_counter()
        for event in runner.run(
            user_id=user_id, session_id=session_id, new_message=content
        ):
            # results embedded in model's response
            if event.is_final_response() and event.content:
                agent_answer = event.content.parts[0].text.strip()
                agent_response['answer'] = agent_answer

        end_time = time.perf_counter()
        print(f"Agent RunTime: <{end_time - start_time}> secs.")

        return session_id, agent_response
    except Exception as error:
        print(f"An error occured during agent invokation or execution.\nError: <{error}>")

        return session_id, agent_response