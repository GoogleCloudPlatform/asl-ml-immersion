# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value
import logging
import os

# Initialize Vertex AI SDK
ENDPOINT_ID = os.getenv("ENDPOINT_ID")
aiplatform.init(project=os.getenv("PROJECT_ID"), location=os.getenv("REGION"))

def explain_fraud_transaction(transaction_features: dict[str, Any]) -> str:
    """
    Calls the Vertex AI Online Prediction endpoint to detect fraud and retrieves
    feature explanations.
    
    Args:
        transaction_features (dict): A dictionary containing transaction features,
        example of input data for transaction: 
        {'customer_id_avg_amount_14day_window': 77.39181818181818,
        'customer_id_avg_amount_15min_window': 198.87,
        'customer_id_avg_amount_1day_window': 43.066764705882356,
        'customer_id_avg_amount_30min_window': 198.87,
        'customer_id_avg_amount_60min_window': 198.87,
        'customer_id_avg_amount_7day_window': 73.41976744186047,
        'customer_id_nb_tx_14day_window': 44.0,
        'customer_id_nb_tx_15min_window': 1.0,
        'customer_id_nb_tx_1day_window': 34.0,
        'customer_id_nb_tx_30min_window': 1.0,
        'customer_id_nb_tx_60min_window': 1.0,
        'customer_id_nb_tx_7day_window': 43.0,
        'terminal_id_avg_amount_15min_window': 103.45,
        'terminal_id_avg_amount_30min_window': 103.45,
        'terminal_id_avg_amount_60min_window': 103.45,
        'terminal_id_nb_tx_14day_window': 0.0,
        'terminal_id_nb_tx_15min_window': 1.0,
        'terminal_id_nb_tx_1day_window': 0.0,
        'terminal_id_nb_tx_30min_window': 1.0,
        'terminal_id_nb_tx_60min_window': 1.0,
        'terminal_id_nb_tx_7day_window': 0.0,
        'terminal_id_risk_14day_window': 0.0,
        'terminal_id_risk_1day_window': 0.0,
        'terminal_id_risk_7day_window': 0.0,
        'tx_amount': 153.8}
    
    Returns:
        str: A natural language summary of the prediction and contributing factors.
    """
    try:
        # Get the endpoint object
        endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)
        
        # Request explanation (not just prediction)
        response = endpoint.explain(instances=[transaction_features])
        
        # --- Parse Prediction Score ---
        # Assuming class '1' is Fraud. The output format in your snippet shows:
        # 'scores': [0.07..., 0.92...] where 0.92 is likely index 1 (Fraud)
        prediction_result = response.predictions[0]
        fraud_score = prediction_result['scores'][1]
        
        # --- Parse Feature Attributions ---
        # Navigating the complex structure from your snippet:
        # explanations -> attributions -> feature_attributions
        explanation = response.explanations[0]
        attributions = explanation.attributions[0]
        
        # Convert Protobuf Struct to a standard Python dict
        features_dict = dict(attributions.feature_attributions)
        
        # Create a list of (feature_name, impact_score)
        feature_impacts = []
        for key, val in features_dict.items():
            # In the raw snippet, value is a list/struct, but the SDK often simplifies it.
            # We handle the raw number extraction safely:
            score = val if isinstance(val, (int, float)) else val.get('number_value', 0.0)
            feature_impacts.append((key, score))
            
        # Sort by absolute impact (magnitude) to find the biggest drivers
        # Positive score = pushes towards Fraud (1), Negative = pushes towards Legit (0)
        top_drivers = sorted(feature_impacts, key=lambda x: abs(x[1]), reverse=True)[:3]

        # --- specific Logic for "tx_amount" ---
        # The agent can explicitly mention amount if it was a factor
        
        # Build the text response
        explanation_text = (
            f"**Risk Assessment:** Score: {fraud_score:.1%}\n\n"
            f"**Why this prediction?**\n"
        )
        
        for name, score in top_drivers:
            direction = "Increased Risk" if score > 0 else "Decreased Risk"
            # Clean up technical feature names for better readability
            readable_name = name.replace("_", " ").title()
            explanation_text += f"- {readable_name}: {direction} (Impact: {score:.3f})\n"

        return explanation_text

    except Exception as e:
        return f"Error calling fraud model: {str(e)}"

# Example Usage Block (for testing)
if __name__ == "__main__":
    # Mock data based on your input snippet's schema
    test_tx = {
        'customer_id_avg_amount_14day_window': 77.39,
        'customer_id_avg_amount_15min_window': 198.87,
        'customer_id_avg_amount_1day_window': 43.06,
        'customer_id_avg_amount_30min_window': 198.87,
        'customer_id_avg_amount_60min_window': 198.87,
        'customer_id_avg_amount_7day_window': 73.41,
        'customer_id_nb_tx_14day_window': 44.0,
        'customer_id_nb_tx_15min_window': 1.0,
        'customer_id_nb_tx_1day_window': 34.0,
        'customer_id_nb_tx_30min_window': 1.0,
        'customer_id_nb_tx_60min_window': 1.0,
        'customer_id_nb_tx_7day_window': 43.0,
        'terminal_id_avg_amount_15min_window': 103.45,
        'terminal_id_avg_amount_30min_window': 103.45,
        'terminal_id_avg_amount_60min_window': 103.45,
        'terminal_id_nb_tx_14day_window': 0.0,
        'terminal_id_nb_tx_15min_window': 1.0,
        'terminal_id_nb_tx_1day_window': 0.0,
        'terminal_id_nb_tx_30min_window': 1.0,
        'terminal_id_nb_tx_60min_window': 1.0,
        'terminal_id_nb_tx_7day_window': 0.0,
        'terminal_id_risk_14day_window': 0.0,
        'terminal_id_risk_1day_window': 0.0,
        'terminal_id_risk_7day_window': 0.0,
        'tx_amount': 153.8
    }
    
    print(predict_fraud_with_explanation(test_tx))
