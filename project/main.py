from google.cloud import storage
import pandas as pd
from simulations.auto_tester.app import run_test
import asyncio
from unittest import result
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from google import genai
from google.adk.tools import VertexAiSearchTool

I_AGENT: LlmAgent = None # Interpreting agent (interprets the results of the scorer)
M_AGENT: LlmAgent = None # Mechanic agent (actually makes the changes to KeyIQ)

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
    retrieved_source = "This is a placeholder retrieved source."
    retrieval_context = "This is a placeholder retrieval context."
    return kiq_answer, retrieved_source, retrieval_context

def get_score_interpretation(scores: dict):
    PROMPT = f"""Interpret the following results:
    {scores}

    If you interpret that the scores indicate a good answer, set the status to 'OK'. Otherwise, set the status to 'NI'.

    Respond with JSON:
    {{'status': <status>, 'interpretation': <interpretation>}}
    """
    # ask the I_AGENT to summarize

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

            kiq_answer, retrieved_source, retrieval_context = get_key_iq_answer(g_question)

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