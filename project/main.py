from google.cloud import storage
import pandas as pd
from simulations.auto_tester.app import run_test
import asyncio
from google.adk.agents import LlmAgent
from simulations.agents.agent_rag.agent import call_rag_agent
import json

from simulations.interpreter_agent.agent import call_interpreter_agent
from metric_config import MetricConfigurations

from dotenv import load_dotenv
load_dotenv()

MAX_LOOPS = 5

# Get & Parse Golden Q&A Doc
def get_golden_qa_doc(uri: str) -> list[dict]:
    client = storage.Client()
    bucket_name, blob_name = uri.replace("gs://", "").split("/", 1)
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    content = blob.download_as_text()
    df = pd.read_csv(pd.compat.StringIO(content))
    golden_qa_list = df.to_dict(orient="records")

    return golden_qa_list

def get_key_iq_answer(question: str) -> tuple[str, str, str]:
    # Placeholder function to get KeyIQ answer, retrieved source, and retrieval context
    # In a real implementation, this would call the KeyIQ system
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
    try:
        asyncio.run(run_vertex_search_example())
    except RuntimeError as error:
        if "cannot be called from a running event loop" in str(error):
            print(f"Skipping execution in running event loop (like Colab/Jupyter). Run locally.")
        else:
            raise error
    return kiq_answer, str(retrieved_sources), str(retrieval_contexts)

def get_score_interpretation(scores: dict):
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

        if response:
            interpretation = response
        
        return interpretation
    
    try:
        interpretation = json.loads(asyncio.run(run_interpreter_agent(PROMPT))[1]['answer'])
        print(f"Intrepretation: {interpretation}")
    except RuntimeError as error:
        if "cannot be called from a running event loop" in str(error):
            print(f"Skipping execution in running event loop (like Colab/Jupyter). Run locally.")
        else:
            raise error
    return interpretation





def invoke_mechanic(interpretations: dict) -> dict[bool, str]:
    # Invokes the mechanic agent
    # Read hyperparameter state
    # Update hyperparameter state
    pass

# For each Golden Q&A:
    # Run Testing Suite
    # If results are not 100% accurate:
        # Move on to the Natural Language Agent to interpret results
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

def main():
    GOLDEN_QA_URI_BUCKET = "gs://keyiq/GoldenQA/"
    GOLDEN_QA_URI_FILE = "golden_qa.csv"

    golden_qa_list = get_golden_qa_doc(GOLDEN_QA_URI_BUCKET + GOLDEN_QA_URI_FILE)
    should_test = True
    loops = 0

    while should_test and loops < MAX_LOOPS:
        final_scores = {}
        for qa in golden_qa_list:
            id = qa["id"]
            g_question = qa["question"]
            g_answer = qa["answer"]
            g_source = qa["source"]

            kiq_answer, retrieved_source, retrieval_context, parameters = get_key_iq_answer(g_question, parameters)

            # Run the testing suite for each Q&A pair
            results = run_test(
                g_question,
                g_answer,
                g_source,
                kiq_answer,
                retrieved_source,
                retrieval_context
            )

            print(f"Results for Q: {g_question}")
            print(results)

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
        
        
    


    

    

    



if __name__ == "__main__":
    print(main())
