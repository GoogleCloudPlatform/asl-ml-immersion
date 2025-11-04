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

async def run_all_rag(golden_qa_list):
    sem = asyncio.Semaphore(RAG_CONC)

    async def one(qa):
        q = qa["question"]
        async with sem:
            return await get_key_iq_answer(q)
        
    tasks = [asyncio.create_task(one(qa)) for qa in golden_qa_list]
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
    should_test = True
    loops = 0

    # Initial State values
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

    # Store the state for each value
    state_list = [State(INIT_TEMPERATURE, INIT_TOP_P, INIT_TOP_K, INIT_SYSTEM_PROMPT, golden_qa_list)]

    while should_test and loops < MAX_LOOPS:
        # use the state finalized in the previous interation
        state = state_list[len(state_list) - 1]

        final_scores = {}
        for qa in state.golden_data:
            id = qa["id"]
            g_question = qa["question"]
            g_answer = qa["answer"]
            g_source = qa["source"]

            kiq_answer, retrieved_source, retrieval_context = get_key_iq_answer(g_question, state)

            # Run the testing suite for each Q&A pair
            results = run_test(
                g_question,
                g_answer,
                g_source,
                kiq_answer,
                retrieved_source,
                retrieval_context
            )

            #print(f"Results for Q: {g_question}")
            #print(results)

            score_interpretation = get_score_interpretation(results)
            print(f"Status: {score_interpretation['status']}")
            print(f"Interpretation: {score_interpretation['interpretation']}")

            if score_interpretation['status'] != 'OK':
                final_scores[id] = score_interpretation['interpretation']

        if len(list(final_scores.keys())) == 0:
            # Interpreter said everything was good
            return {
                'status':'finished',
                'message':f'evaluated to 100% accuracy',
                'results':f'{final_scores}'
            }
        
        # if changing hyper parameters needs to output some sort of text justification as well for the reasons why each parameter changed
        should_test, changes = invoke_mechanic(final_scores)

        print(f'Changes made: {changes}')

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
        
        # finalilze the state for this iteration
        state_list.append(state)
        
    print("\n--- State History ---")
    print(f"<{[state.get_state() for state in state_list]}>")


    

    

    



if __name__ == "__main__":
    print(asyncio.run(main()))
