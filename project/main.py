from __future__ import annotations
from google.cloud import storage
import pandas as pd
from simulations.auto_tester.app import run_test
import asyncio
from simulations.agents.agent_rag.agent import call_rag_agent
import json
import io
import time

from simulations.interpreter_agent.agent import call_interpreter_agent
from simulations.agents.agent_mechanic.agent import call_mechanic_agent
from state import State
from metric_config import MetricConfigurations

from dotenv import load_dotenv
load_dotenv()

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


def _mechanic_call_blocking(interpretations):
    async def _inner():
        return await call_mechanic_agent(interpretations)
    return asyncio.run(_inner())

async def invoke_mechanic(interpretations: dict) -> dict[bool, str]:
    response = await asyncio.to_thread(_mechanic_call_blocking, interpretations)
    
    return response

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

import state
async def main():
    should_test = True
    loops = 0

    GOLDEN_QA_URI_BUCKET = "gs://keyiq/GoldenQA/"
    GOLDEN_QA_URI_FILE = "golden_qa.csv"

    current_state = state.system_state
    current_state.set_golden_data(get_golden_qa_doc(GOLDEN_QA_URI_BUCKET + GOLDEN_QA_URI_FILE))

    while should_test and loops < MAX_LOOPS:
        print(f"--- START LOOP #<{loops}> ----")
        # ---- Phase 1: RAG for all ----
        print("\nRunning the RAG pipeline...", flush=True)
        rag_start = time.perf_counter()
        rag_results = await run_all_rag(current_state.get_golden_data(), current_state)
        rag_end = time.perf_counter()
        print(f"RAG finished in <{round(rag_end - rag_start, 2)}> secs.", flush=True)

        # ---- Phase 2: Tests for all ----
        print("\nTesting all answers...", flush=True)
        test_start = time.perf_counter()
        test_results = await run_all_tests(current_state.get_golden_data(), rag_results, EXP_CONFIG)
        test_end = time.perf_counter()
        print(f"Testing finished in <{round(test_end - test_start, 2)}> secs.", flush=True)

        # ---- Phase 3: Interpreter for all ----
        print("\nInterpreting results...", flush=True)
        interpretations_start = time.perf_counter()
        interpretations = await run_all_interpret(test_results)
        interpretations_end = time.perf_counter()
        print(f"Interpretations finished in <{round(interpretations_end - interpretations_start, 2)}> secs.", flush=True)

        # collect final scores
        final_scores = {
            str(qa["id"]): interp["interpretation"]
            for qa, interp in zip(current_state.get_golden_data(), interpretations)
            if interp["status"] != "OK"
        }

        accuracy = (len(current_state.get_golden_data()) - len(final_scores)) / len(current_state.get_golden_data())
        current_state.set_accuracy(accuracy)

        if not final_scores:
            return {"status": "finished", "message": "evaluated to 100% accuracy", "results": "{}"}
            
        # if changing hyper parameters needs to output some sort of text justification as well for the reasons why each parameter changed
        print(f"\n--- Running Mechanic Agent ---")
        mechanic_start = time.perf_counter()
        await invoke_mechanic(final_scores)
        mechanic_end = time.perf_counter()
        print(f"Mechanic agent finished in <{round(mechanic_end - mechanic_start, 2)}> secs.", flush=True)

        print(f"\nLOOP #<{loops}> OLD STATE:\n{current_state.output_old_state()}")
        print(f"LOOP #<{loops}> NEW STATE:\n{str(current_state.output_state())}")
        print(f"Accuracy: <{accuracy}>")

        print(f"\n--- END LOOP #<{loops}> ---\n")

        if str(current_state.get_old_state()) == str(current_state):
            should_test = False

        current_state.update_old_state()

        if should_test:
            loops += 1

        if not should_test:
            return {
                'status':'finished',
                'message':f'automatic testing stopped',
                'results':f'{final_scores}'
            }

        if loops == MAX_LOOPS:
            return {
                'status':'finished',
                'message':f'max_loops ({MAX_LOOPS}) reached',
                'results':f'{final_scores}'
            }

if __name__ == "__main__":
    print(asyncio.run(main()))
