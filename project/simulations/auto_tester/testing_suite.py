from google import genai
from google.genai.types import GenerateContentConfig, Content, Part
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
    model_name="gemini-2.0-flash-001"
):
    responses = client.models.generate_content(
        model=model_name, contents=prompt, config=GenerateContentConfig(response_mime_type="application/json")
    )
    return responses

class TestingMetricSuite():
    def __init__(self, gemini_client: genai.Client, golden_question, golden_answer, golden_source, key_iq_answer, key_iq_retrieval_context, key_iq_retrieved_source):
        self.gemini_client = gemini_client
        self.golden_question = golden_question
        self.golden_answer = golden_answer
        self.golden_source = golden_source
        self.key_iq_answer = key_iq_answer
        self.key_iq_retrieval_context = key_iq_retrieval_context
        self.key_iq_retrieved_source = key_iq_retrieved_source

    def is_similar(self) -> dict:
        """
        Evaluates the semantic similarity between the KeyIQ answer and the Golden (reference) answer.

        This method uses a large language model (via the configured Gemini client) to assess whether
        the KeyIQ answer sufficiently matches the Golden answer in meaning and content. It constructs
        an evaluation prompt instructing the model to rate the similarity on a scale from 0 to 1, where:

            - 1.0 indicates identical meaning or perfect semantic alignment.
            - 0.0 indicates completely different meanings.
            - Intermediate values represent partial similarity.

        The model is expected to respond with a JSON object containing a numeric similarity score
        and a brief natural language explanation. The response is parsed and returned as a dictionary.

        Example:
            Golden Answer: "The capital of France is Paris."
            KeyIQ Answer: "Paris is the capital city of France."
            → Output: {"similarity_score": 1.0, "explanation": "Both answers convey the same meaning."}

        Returns:
            dict: A dictionary containing:
                - "similarity_score" (float): The evaluated similarity score between 0 and 1.
                - "explanation" (str): A short description justifying the assigned score.

        Raises:
            ValueError: If the model response cannot be parsed as valid JSON.

        """
    
        PROMPT = f"""
        You are an expert evaluator tasked with assessing the similarity between two answers to the same question.
        Your goal is to determine if the KeyIQ answer sufficiently matches the Golden answer in meaning and content.

        Score the similarity from [0, 1], where 1 means the answers are identical in meaning, and 0 means they are completely different.
        For example, if the Golden Answer is "The capital of France is Paris." and the KeyIQ Answer is "Paris is the capital city of France.", you would score it as 1. If the KeyIQ Answer is "The capital of Germany is Berlin.", you would score it as 0. If the KeyIQ Answer is "The capital of France is Lyon.", you might score it as 0.5.

        Score the following:
        Golden Answer: {self.golden_answer}
        KeyIQ Answer: {self.key_iq_answer}

        Respond ONLY with a JSON object in this format:
        {{"similarity_score": <score>, "explanation": "<brief explanation>}}
        """

        answer = generate(PROMPT, self.gemini_client).text
        try:
            similarity_score = json.loads(answer)
        except Exception as e:
            raise ValueError(f"Could not parse similarity score: {e}")
        
        return similarity_score

    def contains_correct_source(self) -> dict:
        """
        Determines whether the source retrieved by KeyIQ matches any of the Golden (reference) sources.

        This method prompts a large language model (via the configured Gemini client) to evaluate whether
        the retrieved source used by KeyIQ is among the correct sources defined in the Golden Source list.
        The model is instructed to respond with a JSON object indicating a boolean result and a brief explanation.

        Specifically:
            - Returns True if the KeyIQ retrieved source is found in or matches any portion of the Golden Source.
            - Returns False otherwise.

        The model is expected to output a JSON object with the following structure:
            {
                "contains_correct_source": <bool>,
                "explanation": "<brief explanation>"
            }

        Example:
            Golden Source: ["document_1.pdf", "document_2.pdf"]
            KeyIQ Retrieved Source: "document_1.pdf"
            → Output: {"contains_correct_source": true, "explanation": "The retrieved source matches a Golden document."}

        Returns:
            dict: A dictionary containing:
                - "contains_correct_source" (bool): True if the retrieved source matches one of the Golden sources, False otherwise.
                - "explanation" (str): A short justification of the determination.

        Raises:
            ValueError: If the model response cannot be parsed as valid JSON.

        """

        PROMPT = f"""
        You are an expert evaluator tasked with determining whether the source retrieved by KeyIQ is correct.
        Answer with "True" if the KeyIQ Retrieved Source is in the list of documents provided by the Golden Source, otherwise answer "False".

        The Golden Source is: {self.golden_source}
        The KeyIQ Retrieved Source is: {self.key_iq_retrieved_source}

        Does the KeyIQ Retrieved Source match any part of the Golden Source?
        Respond ONLY with a JSON object in this format:
        {{"contains_correct_source": <contains_correct_source>, "explanation": "<brief explanation>}}
        """

        generate_config = GenerateContentConfig(
            response_mime_type="application/json"
        )

        answer = generate(PROMPT, self.gemini_client).text
        try:
            contains_correct_source = json.loads(answer)
        except Exception as e:
            raise ValueError(f"Could not parse sources: {e}; answer was: {answer}")

        return contains_correct_source

    def is_answer_grounded(self) -> dict:
        """
        Evaluates whether the KeyIQ answer is grounded in the provided retrieval context.

        This method uses a large language model (via the configured Gemini client) to judge how well
        the KeyIQ answer is supported by the given retrieval context. The model assigns a
        groundedness score between 0 and 1, where:

            - 1.0 means the answer is fully supported by the retrieval context.
            - 0.0 means the answer is not supported at all.
            - Intermediate values represent partial support.

        The evaluator prompt instructs the model to respond with a JSON object containing both the
        numeric score and a short explanation. The response is parsed and returned as a dictionary.

        Example:
            KeyIQ Answer: "The Eiffel Tower is located in Paris, France."
            Retrieval Context: "Paris is home to many landmarks, including the Eiffel Tower."
            → Output: {"groundedness_score": 1.0, "explanation": "The answer is fully supported by the retrieval context."}

        Returns:
            dict: A dictionary containing:
                - "groundedness_score" (float): A value between 0 and 1 indicating how well the answer is supported.
                - "explanation" (str): A brief natural-language justification for the score.

        Raises:
            ValueError: If the model response cannot be parsed as valid JSON.

        """
        PROMPT = f"""
        You are an expert evaluator tasked with determining whether the KeyIQ answer is grounded in the provided retrieval context.
        Your goal is to determine if the KeyIQ answer is supported by the information in the retrieval context.
        Score the groundedness from [0, 1], where 1 means the answer is fully supported by the retrieval context, and 0 means it is not supported at all.
        For example, if the retrieval context contains all the information needed to answer the question accurately, you would score it as 1. If the retrieval context is completely unrelated to the question, you would score it as 0. If the retrieval context provides some relevant information but not enough for a complete answer, you might score it as 0.5.

        Score the following:
        KeyIQ Answer: {self.key_iq_answer}
        Retrieval Context: {self.key_iq_retrieval_context}

        Respond ONLY with a JSON object in this format:
        {{"groundedness_score": <score>, "explanation": "<brief explanation>}}
        """

        answer = generate(PROMPT, self.gemini_client).text
        try:
            groundedness_score = json.loads(answer)
        except Exception as e:
            raise ValueError(f"Could not parse groundedness_score: {e}")
        
        return groundedness_score

    def is_retrieval_relevant(self) -> dict:
        """
        Evaluates how relevant the KeyIQ retrieval context is to the Golden (reference) question.

        This method prompts a large language model (via the configured Gemini client) to assess
        whether the retrieval context provided by KeyIQ contains information pertinent to answering
        the Golden Question. The model scores the relevance on a scale from 0 to 1, where:

            - 1.0 indicates the retrieval context is highly relevant and directly addresses the question.
            - 0.0 indicates the retrieval context is completely unrelated.
            - Intermediate values represent partial relevance.

        The evaluator is instructed to respond with a JSON object containing a numeric relevance
        score and a brief explanation. The response is parsed and returned as a dictionary.

        Example:
            Golden Question: "What is the capital of France?"
            Retrieval Context: "Paris is the capital and largest city of France."
            → Output: {"relevance_score": 1.0, "explanation": "The context directly answers the question."}

        Returns:
            dict: A dictionary containing:
                - "relevance_score" (float): A value between 0 and 1 indicating the relevance of the retrieval context.
                - "explanation" (str): A concise justification for the assigned relevance score.

        Raises:
            ValueError: If the model response cannot be parsed as valid JSON.

        """
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
        {{"relevance_score": <score>, "explanation": "<brief explanation>}}
        """

        answer = generate(PROMPT, self.gemini_client).text
        try:
            relevance_score = json.loads(answer)
        except Exception as e:
            raise ValueError(f"Could not parse relevance_score: {e}")
        
        return relevance_score
    
    def perform_quality_checks(self) -> str:
        """
        Evaluates the overall linguistic and structural quality of the KeyIQ answer.

        This method uses a pointwise evaluation metric to assess the KeyIQ answer across four key
        dimensions: fluency, concision, clarity, and single-purpose focus. Each criterion is defined
        in a `PointwiseMetricPromptTemplate` that instructs a large language model to score the
        response according to a rubric ranging from -2 to 2:

            - **2:** The response excels in all criteria.
            - **1:** The response meets most criteria well.
            - **0:** The response meets some criteria but has notable issues.
            - **-1:** The response struggles with several criteria.
            - **-2:** The response fails to meet any of the criteria effectively.

        The evaluation is run as an experiment using the `EvalTask` framework with a single metric,
        `"text_quality"`, applied to the KeyIQ answer. The resulting average text quality score is
        extracted from the evaluation summary and returned as a stringified float.

        Example:
            → Output: `"1.0"`

        Returns:
            str: The mean text quality score (as a stringified float) derived from the evaluation results.

        Raises:
            KeyError: If the expected `'text_quality/mean'` key is missing from the evaluation summary.
            Exception: If the evaluation process fails or returns an invalid result.

        """
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

        return str(float(results.summary_metrics['text_quality/mean']))

