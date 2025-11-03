from simulations.auto_tester.testing_suite import TestingMetricSuite
from google import genai


def run_test(g_question, g_answer, g_source, kiq_answer, retrieved_source, retrieval_context):
    """
    Run the testing suite for a single test case.

    Args:
        g_question (str): The golden question.
        g_answer (str): The golden answer.
        g_source (str): The golden source.
        kiq_answer (str): The KeyIQ answer.
        retrieved_source (str): The source retrieved by KeyIQ.
        retrieval_context (str): The retrieval context used by KeyIQ.

    Returns:
        dict: A dictionary containing the results of various quality checks.

    """

    testing_suite = TestingMetricSuite(
        gemini_client=genai.Client(vertexai=True, location="us-central1"),
        golden_question=g_question,
        golden_answer=g_answer,
        golden_source=g_source,
        key_iq_answer=kiq_answer,
        key_iq_retrieval_context=retrieval_context,
        key_iq_retrieved_source=retrieved_source
    )

    results = {
        "is_similar": testing_suite.is_similar(),
        "contains_correct_source": testing_suite.contains_correct_source(),
        "is_answer_grounded": testing_suite.is_answer_grounded(),
        "is_retrieval_relevant": testing_suite.is_retrieval_relevant(),
        "quality_score": testing_suite.perform_quality_checks()
    }

    return results
