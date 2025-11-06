class MetricConfigurations():
    METRIC_DESCRIPTIONS = {
        "is_similar": "Evaluates the semantic similarity between the KeyIQ answer and the Golden (reference) answer.",
        "contains_correct_source": "Determines whether the source retrieved by KeyIQ matches any of the Golden (reference) sources.",
        "is_answer_grounded": "Evaluates whether the KeyIQ answer is grounded in the provided retrieval context.",
        "is_retrieval_relevant": "Evaluates how relevant the KeyIQ retrieval context is to the Golden (reference) question.",
        # "quality_score": "Evaluates the overall linguistic and structural quality of the KeyIQ answer."
    }
    SCORING_THRESHOLDS = {
        "is_similar": {
            "high": 0.70,
            "medium": 0.40,
            "low": 0.00,
        },
        "contains_correct_source": {
            "true": 1.0,
            "false": 0.0,
        },
        "is_answer_grounded": {
            "high": 0.70,
            "medium": 0.40,
            "low": 0.00,
        },
        "is_retrieval_relevant": {
            "high": 0.80,
            "medium": 0.50,
            "low": 0.00,
        },
        # "text_quality": {
        #     "excellent": 1.5,
        #     "good": 0.5,
        #     "fair": -0.49,
        #     "poor": -0.5,
        # },
    }