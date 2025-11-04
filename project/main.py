from __future__ import annotations
from google.cloud import storage
import pandas as pd
from simulations.auto_tester.app import run_test
import asyncio
from simulations.agents.agent_rag.agent import call_rag_agent
import json
import io

from simulations.interpreter_agent.agent import call_interpreter_agent
from state import State
from metric_config import MetricConfigurations

from dotenv import load_dotenv
load_dotenv()

INIT_TEMPERATURE = 0.1
INIT_TOP_P = 0.3
INIT_TOP_K = 40
INIT_SYSTEM_PROMPT = """
    <PERSONA>
        You are an english literature academic with expertise on old english books.
    </PERSONA>
    <INSTRUCTIONS>
        1. Use the vertexai serach tool to find information relevant to the question you are asked.
        2. Use the relevant information you found to answer the question.
    <RULES>
        1. Only use data in the datastore to answer questions.
    </RULES>
    <TONE>
        1. Answer should be clear and concise.
        2. Answers should have an english literature academic tone and focus
    </TONE>
"""

MAX_LOOPS = 5

RAG_CONC = 16
TEST_CONC = 10
INTERP_CONC = 16

EXP_CONFIG = {
    "experiment":"quality-checks-experiment",
    "region":"us-central1",
    "project_id":"qwiklabs-asl-00-58d3f08e551b"
}

# Get & Parse Golden Q&A Doc
def get_golden_qa_doc(uri: str) -> list[dict]:
    client = storage.Client()
    bucket_name, blob_name = uri.replace("gs://", "").split("/", 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    content = blob.download_as_text()
    df = pd.read_csv(io.StringIO(content))
    golden_qa_list = df.to_dict(orient="records")

    id_c = 1
    for question in golden_qa_list:
        question["id"] = id_c
        id_c += 1

    return golden_qa_list

def _rag_call_blocking(question: str, state: State):
    async def _inner():
        return await call_rag_agent(question, state)
    return asyncio.run(_inner())

async def get_key_iq_answer(question: str, state: State) -> tuple[str, str, str]:
    # Placeholder function to get KeyIQ answer, retrieved source, and retrieval context
    # In a real implementation, this would call the KeyIQ system
    response = await asyncio.to_thread(_rag_call_blocking, question, state)

    kiq_answer = "This is a placeholder KeyIQ answer."
    retrieved_sources = []
    retrieval_contexts = []

    if response:
        kiq_answer = response['answer']
        for context in response['context']:
                retrieved_sources.append(context['source'])
                retrieval_contexts.append(context['text'])

    return kiq_answer, str(retrieved_sources), str(retrieval_contexts)

def _interpreter_call_blocking(prompt, parameters):
    async def _inner():
        return await call_interpreter_agent(prompt, parameters=parameters)
    return asyncio.run(_inner())

async def get_score_interpretation(scores: dict):
    PROMPT = f"""Interpret the following results:
    {scores}

    If you interpret that the scores indicate a good answer, set the status to 'OK'. Otherwise, set the status to 'NI'.
    """

    interpretation = {"message":"This is a placeholder interpretation."}
    parameters={
        'metric_descriptions':str(MetricConfigurations.METRIC_DESCRIPTIONS),
        'scoring_thresholds':str(MetricConfigurations.SCORING_THRESHOLDS)
    }

    response = await asyncio.to_thread(_interpreter_call_blocking, PROMPT, parameters)

    if response:
        interpretation = response[1]['answer']
    
    return json.loads(interpretation)





def invoke_mechanic(interpretations: dict) -> dict[bool, str]:
    # Invokes the mechanic agent
    # Read hyperparameter state
    # Update hyperparameter state
    pass

# For each Golden Q&A:
    # Run Testing Suite
    # If results are not 100% accurate:
        # Move on to the Na(tural Language Agent to interpret results
        # Add interpreted results to a list of interpreted results associated with this Golden Q&A
    # Else:
        # Stop

# Move to the Mechanic Agent to suggest changes based on composite interpreted results
    # Tools available:
        # Change Hyperparameters
        # Alter Golden Q&A

# If the mechanic agent made changes:
    # Rerun steps from the top
# Else:
    # Stop and output final Q&A document, testing results, and hyperparameters

async def run_all_rag(golden_qa_list, current_state: State):
    sem = asyncio.Semaphore(RAG_CONC)

    async def one(qa, state):
        q = qa["question"]
        async with sem:
            return await get_key_iq_answer(q, state)
        
    tasks = [asyncio.create_task(one(qa, current_state)) for qa in golden_qa_list]
    return await asyncio.gather(*tasks)

async def run_all_tests(
    golden_qa_list,
    rag_results,
    exp_cfg,
):
    sem = asyncio.Semaphore(TEST_CONC)

    async def one(qa, rag):
        gq, ga, gs = qa["question"], qa["answer"], qa["source"]
        kiq_answer, retrieved_source, retrieval_context = rag
        args = (gq, ga, gs, kiq_answer, retrieved_source, retrieval_context, exp_cfg)
        async with sem:
            return await asyncio.to_thread(run_test, *args)

    tasks = [asyncio.create_task(one(qa, rag)) for qa, rag in zip(golden_qa_list, rag_results)]
    return await asyncio.gather(*tasks)

async def run_all_interpret(test_results):
    sem = asyncio.Semaphore(INTERP_CONC)

    async def one(res):
        async with sem:
            interp = await get_score_interpretation(res)
            status = interp.get("status", "NI")
            return {"status": status, "interpretation": interp.get("interpretation", ""), "_raw": interp}

    return await asyncio.gather(*[asyncio.create_task(one(r)) for r in test_results])

async def main():
    GOLDEN_QA_URI_BUCKET = "gs://keyiq/GoldenQA/"
    GOLDEN_QA_URI_FILE = "golden_qa.csv"
    current_state = State(INIT_TEMPERATURE, INIT_TOP_P, INIT_TOP_K, INIT_SYSTEM_PROMPT, get_golden_qa_doc(GOLDEN_QA_URI_BUCKET + GOLDEN_QA_URI_FILE))

    # ---- Phase 1: RAG for all ----
    print("Running all rag...", flush=True)
    rag_results = await run_all_rag(current_state.get_golden_data(), current_state)

    # ---- Phase 2: Tests for all ----
    print("Running all tests...", flush=True)
    test_results = await run_all_tests(current_state.get_golden_data(), rag_results, EXP_CONFIG)

    # ---- Phase 3: Interpreter for all ----
    print("Running all interpretations...", flush=True)
    interpretations = await run_all_interpret(test_results)

    # collect final scores
    final_scores = {
        str(qa["id"]): interp["interpretation"]
        for qa, interp in zip(current_state.get_golden_data(), interpretations)
        if interp["status"] != "OK"
    }

    if not final_scores:
        return {"status": "finished", "message": "evaluated to 100% accuracy", "results": "{}"}
    
    return "Done"
        
    # if changing hyper parameters needs to output some sort of text justification as well for the reasons why each parameter changed
    # should_test = invoke_mechanic(final_scores)
    # print(f"Old State: {current_state.get_old_state()}")
    # print(f"New State: {str(current_state)}")

    # if should_test:
    #     loops += 1

    # if not should_test:
    #     return {
    #         'status':'finished',
    #         'message':f'automatic testing stopped',
    #         'results':f'{final_scores}'
    #     }

    # if loops == MAX_LOOPS:
    #     return {
    #         'status':'finished',
    #         'message':f'max_loops ({MAX_LOOPS}) reached',
    #         'results':f'{final_scores}'
    #     }

if __name__ == "__main__":
    print(asyncio.run(main()))
