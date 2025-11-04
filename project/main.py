from __future__ import annotations
from google.cloud import storage
import pandas as pd
from simulations.auto_tester.app import run_test
import asyncio
from google.adk.agents import LlmAgent
from simulations.agents.agent_rag.agent import call_rag_agent
import json
import io
from google.cloud import aiplatform
import time

import functools

from simulations.interpreter_agent.agent import call_interpreter_agent
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

def _rag_call_blocking(question: str):
    async def _inner():
        return await call_rag_agent(question, 0.9, 0.3, 40)
    return asyncio.run(_inner())

async def get_key_iq_answer(question: str) -> tuple[str, str, str]:
    # Placeholder function to get KeyIQ answer, retrieved source, and retrieval context
    # In a real implementation, this would call the KeyIQ system
    response = await asyncio.to_thread(_rag_call_blocking, question)
    
    kiq_answer = "This is a placeholder KeyIQ answer."
    retrieved_sources = []
    retrieval_contexts = []

    async def run_vertex_search_example():
        nonlocal kiq_answer, retrieved_sources, retrieval_contexts

        # If calling follow-ups need to pass the session_id
        ## TODO: replace temperature, top_p, top_k values with state
        response = await call_rag_agent(question, 0.9, 0.3, 40)

        if response:
            kiq_answer = response['answer']

            for context in response['context']:
                retrieved_sources.append(context['source'])
                retrieval_contexts.append(context['text'])
    # try:
    #     asyncio.run(run_vertex_search_example())
    # except RuntimeError as error:
    #     if "cannot be called from a running event loop" in str(error):
    #         print(f"Skipping execution in running event loop (like Colab/Jupyter). Run locally.")
    #     else:
    #         raise error
    await run_vertex_search_example()

    return kiq_answer, str(retrieved_sources), str(retrieval_contexts)

async def get_score_interpretation(scores: dict):
    PROMPT = f"""Interpret the following results:
    {scores}

    If you interpret that the scores indicate a good answer, set the status to 'OK'. Otherwise, set the status to 'NI'.

    Respond with JSON:
    {{'status': <status>, 'interpretation': <interpretation>}}
    """

    interpretation = {"message":"This is a placeholder interpretation."}

    async def run_interpreter_agent(prompt, parameters={
        'metric_descriptions':str(MetricConfigurations.METRIC_DESCRIPTIONS),
        'scoring_thresholds':str(MetricConfigurations.SCORING_THRESHOLDS)
    }):
        
        response = await call_interpreter_agent(prompt, parameters=parameters)

        # if not isinstance(response, (dict)):
        #     raise TypeError(
        #         f"Agent return a {type(response).__name__} instead of dict. "
        #         f"Raw response: {response!r}"
        #     )

        if response:
            interpretation = response[1]['answer']
        
        return interpretation
    

    response = await run_interpreter_agent(PROMPT)
    interpretation = json.loads(response)
        
    return interpretation





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

# async def process_one_qa(
#     qa: dict,
#     rag_sem: asyncio.Semaphore,
#     test_sem: asyncio.Semaphore,
#     interp_sem: asyncio.Semaphore
# ) -> tuple[str, dict, dict]:
#     """
#     Runs the full pipeline for a single Q&A:
#     - KeyIQ answer (async)
#     - run_test (blocking -> thread)
#     - interpretation (async)
#     Returns:
#         (id, results, interpretation) where interpretation is None if status=='OK'
#     """

#     qa_id = str(qa["id"])
#     g_question = qa["question"]
#     g_answer = qa["answer"]
#     g_source = qa["source"]

#     t0 = time.time()
#     print(f"[{qa_id}] RAG start", flush=True)
#     async with rag_sem:
#         try:
#             kiq_answer, retrieved_source, retrieval_context = await get_key_iq_answer(g_question)
#         except RuntimeError:
#             raise
#     print(f"[{qa_id}] RAG done in {time.time()-t0:.2f}s", flush=True)

#     t1 = time.time()
#     print(f"[{qa_id}] Tests start", flush=True)
#     async with test_sem:
#         results = await asyncio.to_thread(
#             run_test,
#             g_question,
#             g_answer,
#             g_source,
#             kiq_answer,
#             retrieved_source,
#             retrieval_context,
#             EXP_CONFIG
#         )

#     print

#         score_interpretation = await get_score_interpretation(results)

#         try:
#             print(f"Status: {score_interpretation['status']}")
#             print(f"Interpretation: {score_interpretation.get('interpretation', '')}")
#         except Exception as e:
#             print(f"Error: {e}")

#         if score_interpretation['status'] != "OK":
#             return qa_id, results, score_interpretation
        
#         return qa_id, results, None

# --- Phase 1: RAG for all ---
async def run_all_rag(golden_qa_list):
    sem = asyncio.Semaphore(RAG_CONC)

    async def one(qa):
        q = qa["question"]
        async with sem:
            return await get_key_iq_answer(q)  # your existing async fn
        
    tasks = [asyncio.create_task(one(qa)) for qa in golden_qa_list]
    return await asyncio.gather(*tasks)

# --- Phase 2: Tests for all ---
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
            # run_test signature ends with EXP_CONFIG in your code
            # but we use a wrapper to create a run per thread
            return await asyncio.to_thread(run_test, args[:-1])

    tasks = [asyncio.create_task(one(qa, rag)) for qa, rag in zip(golden_qa_list, rag_results)]
    return await asyncio.gather(*tasks)

# --- Phase 3: Interpreter for all ---
async def run_all_interpret(test_results):
    sem = asyncio.Semaphore(INTERP_CONC)

    async def one(res):
        async with sem:
            interp = await get_score_interpretation(res)  # your async fn
            # normalize shape
            status = interp.get("status", "NI")
            return {"status": status, "interpretation": interp.get("interpretation", ""), "_raw": interp}

    return await asyncio.gather(*[asyncio.create_task(one(r)) for r in test_results])

async def main():
    GOLDEN_QA_URI_BUCKET = "gs://keyiq/GoldenQA/"
    GOLDEN_QA_URI_FILE = "golden_qa.csv"
    golden_qa_list = get_golden_qa_doc(GOLDEN_QA_URI_BUCKET + GOLDEN_QA_URI_FILE)

    # ---- Phase 1: RAG for all ----
    print("Running all rag...", flush=True)
    rag_results = await run_all_rag(golden_qa_list)

    # ---- Phase 2: Tests for all ----
    print("Running all tests...", flush=True)
    test_results = await run_all_tests(golden_qa_list, rag_results, EXP_CONFIG)

    # ---- Phase 3: Interpreter for all ----
    print("Running all interpretations...", flush=True)
    interpretations = await run_all_interpret(test_results)

    # collect final scores
    final_scores = {
        str(qa["id"]): interp["interpretation"]
        for qa, interp in zip(golden_qa_list, interpretations)
        if interp["status"] != "OK"
    }

    if not final_scores:
        return {"status": "finished", "message": "evaluated to 100% accuracy", "results": "{}"}
    return {"status": "finished", "message": "completed staged run", "results": f"{final_scores}"}

        
        # should_test, changes = invoke_mechanic(final_scores)

        # print(f'Changes made: {changes}')

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

    print("Final Results:")
    print(final_scores)
        
        
    


    

    

    



if __name__ == "__main__":
    print(asyncio.run(main()))
