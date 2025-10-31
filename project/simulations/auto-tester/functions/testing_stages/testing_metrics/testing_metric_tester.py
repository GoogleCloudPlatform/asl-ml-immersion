import pytest
import json
from testing_metric_suite import TestingMetricSuite  # Replace with actual import path

@pytest.fixture
def mock_gemini_client():

@pytest.fixture
def suite(mock_gemini_client):
    return TestingMetricSuite(
        gemini_client=mock_gemini_client,
        golden_question="What is the capital of France?",
        golden_answer="Paris.",
        golden_source="source1",
        key_iq_question="What is the capital of France?",
        key_iq_answer="Paris.",
        key_iq_retrieval_context="Paris is the capital of France.",
        key_iq_retrieved_source="source1"
    )

@patch("your_module.generate")
def test_is_similar(mock_generate, suite):
    mock_generate.return_value = json.dumps({"similarity_score": 1.0})
    assert suite.is_similar() == 1.0

@patch("your_module.generate")
def test_contains_correct_source(mock_generate, suite):
    mock_generate.return_value = json.dumps({"contains_correct_source": True})
    assert suite.contains_correct_source() is True

@patch("your_module.generate")
def test_is_answer_grounded(mock_generate, suite):
    mock_generate.return_value = json.dumps({"groundedness_score": 0.8})
    assert suite.is_answer_grounded() == 0.8

@patch("your_module.generate")
def test_is_retrieval_relevant(mock_generate, suite):
    mock_generate.return_value = json.dumps({"relevance_score": 1.0})
    assert suite.is_retrieval_relevant() == 1.0

def test_perform_quality_checks(suite):
    # You may want to mock EvalTask and related objects for a full test
    # Here, just check that it runs and returns something
    result = suite.perform_quality_checks()
    assert result is not None