from google import genai
from google.genai.types import Content, Part
import pandas as pd
import json

from vertexai.evaluation import (
    EvalTask,
    MetricPromptTemplateExamples,
    PairwiseMetric,
    PointwiseMetric,
    PointwiseMetricPromptTemplate,
)

def generate(
    prompt: str,
    client: genai.Client,
    model_name="gemini-2.0-flash-001",
):
    responses = client.models.generate_content(
        model=model_name, contents=prompt
    )
    return responses

class TestingMetricSuite():
    def __init__(self, gemini_client: genai.Client, golden_question, golden_answer, golden_source, key_iq_question, key_iq_answer, key_iq_retrieval_context, key_iq_retrieved_source):
        self.gemini_client = gemini_client
        self.golden_question = golden_question
        self.golden_answer = golden_answer
        self.golden_source = golden_source
        self.key_iq_question = key_iq_question
        self.key_iq_answer = key_iq_answer
        self.key_iq_retrieval_context = key_iq_retrieval_context
        self.key_iq_retrieved_source = key_iq_retrieved_source

    def is_similar(self) -> float:
    # Placeholder similarity check
        PROMPT = f"""
        You are an expert evaluator tasked with assessing the similarity between two answers to the same question.
        Your goal is to determine if the KeyIQ answer sufficiently matches the Golden answer in meaning and content.

        Score the similarity from [0, 1], where 1 means the answers are identical in meaning, and 0 means they are completely different.
        For example, if the Golden Answer is "The capital of France is Paris." and the KeyIQ Answer is "Paris is the capital city of France.", you would score it as 1. If the KeyIQ Answer is "The capital of Germany is Berlin.", you would score it as 0. If the KeyIQ Answer is "The capital of France is Lyon.", you might score it as 0.5.

        Score the following:
        Golden Answer: {self.golden_answer}
        KeyIQ Answer: {self.key_iq_answer}

        Respond ONLY with a JSON object in this format:
        {{"similarity_score": <score>}}
        """

        answer = generate(PROMPT, self.gemini_client)
        try:
            similarity_score = json.loads(answer)["similarity_score"]
        except Exception as e:
            raise ValueError(f"Could not parse similarity score: {e}")
        
        return similarity_score

    def contains_correct_source(self) -> bool:
        PROMPT = f"""
        You are an expert evaluator tasked with determining whether the source retrieved by KeyIQ is correct.
        Answer with "True" if the KeyIQ Retrieved Source is in the list of documents provided by the Golden Source, otherwise answer "False".

        The Golden Source is: {self.golden_source}
        The KeyIQ Retrieved Source is: {self.key_iq_retrieved_source}

        Does the KeyIQ Retrieved Source match any part of the Golden Source?
        Respond ONLY with a JSON object in this format:
        {{"contains_correct_source": <contains_correct_source>}}
        """

        answer = generate(PROMPT, self.gemini_client)
        try:
            contains_correct_source = json.loads(answer)["contains_correct_source"]
        except Exception as e:
            raise ValueError(f"Could not parse sources: {e}")

        return contains_correct_source

    def is_answer_grounded(self) -> float:
        PROMPT = f"""
        You are an expert evaluator tasked with determining whether the KeyIQ answer is grounded in the provided retrieval context.
        Your goal is to determine if the KeyIQ answer is supported by the information in the retrieval context.
        Score the groundedness from [0, 1], where 1 means the answer is fully supported by the retrieval context, and 0 means it is not supported at all.
        For example, if the retrieval context contains all the information needed to answer the question accurately, you would score it as 1. If the retrieval context is completely unrelated to the question, you would score it as 0. If the retrieval context provides some relevant information but not enough for a complete answer, you might score it as 0.5.

        Score the following:
        KeyIQ Answer: {self.key_iq_answer}
        Retrieval Context: {self.key_iq_retrieval_context}

        Respond ONLY with a JSON object in this format:
        {{"groundedness_score": <score>}}
        """

        answer = generate(PROMPT, self.gemini_client)
        try:
            groundedness_score = json.loads(answer)["groundedness_score"]
        except Exception as e:
            raise ValueError(f"Could not parse groundedness_score: {e}")
        
        return groundedness_score

    def is_retrieval_relevant(self) -> float:
        PROMPT = f"""
        You are an expert evaluator tasked with determining whether the KeyIQ provided retrieval context is relevant to the Golden Question.
        Your goal is to determine if the retrieval context contains information pertinent to answering the Golden Question.
        Score the relevance from [0, 1], where 1 means the retrieval context is highly relevant to the question, and 0 means it is completely irrelevant.
        If the retrieval context directly addresses the topic of the question, you would score it as 1. If the retrieval context is about a completely different topic, you would score it as 0. If the retrieval context is somewhat related but does not fully address the question, you might score it as 0.5.
        For example, if the Golden Question is "What is the capital of France?" and the retrieval context discusses Paris and its significance, you would score it as 1. If the retrieval context talks about the geography of Germany, you would score it as 0. If it mentions European capitals in general without focusing on France, you might score it as 0.5.

        Score the following:
        Golden Question: {self.golden_question}
        Retrieval Context: {self.key_iq_retrieval_context}
        Respond ONLY with a JSON object in this format:
        {{"relevance_score": <score>}}
        """

        answer = generate(PROMPT, self.gemini_client)
        try:
            relevance_score = json.loads(answer)["relevance_score"]
        except Exception as e:
            raise ValueError(f"Could not parse relevance_score: {e}")
        
        return relevance_score
    
    def perform_quality_checks(self):
        metric_prompt_template = PointwiseMetricPromptTemplate(
            criteria={
                "fluency": "The response is well-formed, grammatically correct, and flows naturally, making it easy to read and understand.",
                "concision": "The response is brief and to the point, avoiding unnecessary words or overly complex sentences while still conveying the full meaning.",
                "clarity": "The response is easy to understand, free from ambiguity, and effectively communicates the intended message.",
                "single-purpose": "The response focuses on a single topic or idea, avoiding unnecessary tangents or multiple subjects that could confuse the reader.",
            },
            rating_rubric={
                "2": "The response excels in all criteria.",
                "1": "The response meets most criteria well.",
                "0": "The response meets some criteria but has notable issues.",
                "-1": "The response struggles with several criteria.",
                "-2": "The response fails to meet any of the criteria effectively."
            },
        )

        text_quality = PointwiseMetric(
            metric="text_quality",
            metric_prompt_template=metric_prompt_template,
        )

        eval_dataset = pd.DataFrame(
        {
            "response": [self.key_iq_answer],
        }
)

        EXPERIMENT_NAME = "quality-checks-experiment"
        eval_task = EvalTask(
            dataset=eval_dataset, metrics=[text_quality], experiment=EXPERIMENT_NAME
        )
        results = eval_task.evaluate()

        return results.summary_metrics

