from google.cloud import storage
import pandas as pd
import io

from testing_metrics.testing_metric_suite import TestingMetricSuite

def get_csv_from_gcs(bucket_name, blob_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    data = blob.download_as_bytes()
    return pd.read_csv(io.BytesIO(data))


def get_testing_results(keyiq_bucket_uri):
    GOLDEN_QUESTION_COL = 0
    GOLDEN_ANSWER_COL = 1
    GOLDEN_SOURCE_COL = 2
    KEYIQ_QUESTION_COL = 3
    KEYIQ_ANSWER_COL = 4
    RETRIEVED_SOURCE_COL = 5
    RETRIEVAL_CONTEXT_COL = 6
    
    # Placeholder function to simulate fetching testing results
    # Step 1: Fetch the csv from the KeyIQ bucket URI from GCS
    bucket_name = 'keyiq'
    blob_name = keyiq_bucket_uri.replace(f'gs://{bucket_name}/', '')
    data = get_csv_from_gcs(bucket_name, blob_name)

    # Step 2: Process the csv to extract the golden questions, golden answers, keyiq questions, and keyiq answers
    processed_results = []
    for idx, row in data.iterrows():
        golden_question = row[GOLDEN_QUESTION_COL]
        golden_answer = row[GOLDEN_ANSWER_COL]
        golden_source = row[GOLDEN_SOURCE_COL]
        keyiq_question = row[KEYIQ_QUESTION_COL]
        keyiq_answer = row[KEYIQ_ANSWER_COL]
        retrieved_source = row[RETRIEVED_SOURCE_COL]
        retrieval_context = row[RETRIEVAL_CONTEXT_COL]
        processed_results.append({
            "golden_question": golden_question,
            "golden_answer": golden_answer,
            "keyiq_question": keyiq_question,
            "keyiq_answer": keyiq_answer,
            "golden_source": golden_source,
            "retrieved_source": retrieved_source,
            "retrieval_context": retrieval_context
        })

    # Step 3: Compare each answer with a series of functions
    for row in processed_results:
        testing_suite = TestingMetricSuite(
            golden_question=row["golden_question"],
            golden_answer=row["golden_answer"],
            golden_source=row["golden_source"],
            key_iq_question=row["keyiq_question"],
            key_iq_answer=row["keyiq_answer"],
            key_iq_retrieval_context=row["retrieval_context"],
            key_iq_retrieved_source=row["retrieved_source"]
        )

        row["is_similar"] = testing_suite.is_similar()
        row["contains_correct_source"] = testing_suite.contains_correct_source()
        row["is_answer_grounded"] = testing_suite.is_answer_grounded()
        row["is_retrieval_relevant"] = testing_suite.is_retrieval_relevant()

    # Step 4: Return the testing results as a list of dictionaries
    return 1, processed_results