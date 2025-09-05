# Copyright 2022 Google, LLC.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import base64
import os
import json
from flask import Flask, request
from google.cloud import aiplatform as aiplatform
from google.cloud import pubsub_v1
from google.cloud.aiplatform import Featurestore, EntityType, Feature

# Retrieve environment variables
PROJECT_ID = os.environ.get('PROJECT_ID', 
                            'PROJECT_ID variable is not set.')
ENDPOINT_ID = os.environ.get('ENDPOINT_ID', 
                             'ENDPOINT_ID variable is not set.')
FEATURESTORE_ID = os.environ.get('FEATURESTORE_ID', 
                                 'FEATURESTORE_ID variable is not set.')
REGION = os.environ.get('REGION', 
                        'REGION variable is not set.')


app = Flask(__name__)

PAYLOAD_SCHEMA = {
    "tx_amount": "float64",
    "customer_id_nb_tx_1day_window": "int64",
    "customer_id_nb_tx_7day_window": "int64",
    "customer_id_nb_tx_14day_window": "int64",
    "customer_id_avg_amount_1day_window": "float64",
    "customer_id_avg_amount_7day_window": "float64",
    "customer_id_avg_amount_14day_window": "float64",
    "customer_id_nb_tx_15min_window": "int64",
    "customer_id_avg_amount_15min_window": "float64", 
    "customer_id_nb_tx_30min_window": "int64",
    "customer_id_avg_amount_30min_window": "float64", 
    "customer_id_nb_tx_60min_window": "int64",
    "customer_id_avg_amount_60min_window":"float64", 
    "terminal_id_nb_tx_1day_window": "int64",
    "terminal_id_nb_tx_7day_window": "int64",
    "terminal_id_nb_tx_14day_window": "int64",
    "terminal_id_risk_1day_window": "float64",
    "terminal_id_risk_7day_window": "float64",
    "terminal_id_risk_14day_window": "float64",
    "terminal_id_nb_tx_15min_window": "int64",
    "terminal_id_avg_amount_15min_window": "float64", 
    "terminal_id_nb_tx_30min_window": "int64",
    "terminal_id_avg_amount_30min_window":"float64", 
    "terminal_id_nb_tx_60min_window": "int64",
    "terminal_id_avg_amount_60min_window": "float64"
}


# Instantiate Vertex AI Feature Store object
try:
    ff_feature_store = Featurestore(FEATURESTORE_ID)
except NameError:
    print(f"""The feature store {FEATURESTORE_ID} does not exist!""")

# Instantiate the Vertex AI endpoint object
aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint_obj = aiplatform.Endpoint(ENDPOINT_ID)

def features_lookup(ff_feature_store, entity, entity_ids):
    '''
    Function that retrieves feature values from Vertex AI Feature Store
    '''
    entity_type = ff_feature_store.get_entity_type(entity)
    aggregated_features = entity_type.read(entity_ids=entity_ids,feature_ids="*")
    aggregated_features_preprocessed = preprocess(aggregated_features)
    features = aggregated_features_preprocessed.iloc[0].to_dict()
    return features

def preprocess(payload):
    '''
    Function that pre-processes the payload values
    '''
    # replace NaN's
    for key , value in payload.items():
        if value is None:
            payload[key] = 0.0
    return payload
    
@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    pubsub_message = envelope["message"]


    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        payload_input = base64.b64decode(pubsub_message["data"]).decode("utf-8").strip()
        print(f" >> payload input {payload_input}!")
        # parse payload string into JSON object
        payload_json = json.loads(payload_input)
        
        payload={}
        payload["tx_amount"] = payload_json["TX_AMOUNT"]
        
        # look up the customer features from Vertex AI Feature Store        
        customer_features = features_lookup(ff_feature_store, "customer",[payload_json["CUSTOMER_ID"]])
        payload["customer_id_nb_tx_1day_window"] = customer_features["customer_id_nb_tx_1day_window"]
        payload["customer_id_nb_tx_7day_window"] = customer_features["customer_id_nb_tx_7day_window"]
        payload["customer_id_nb_tx_14day_window"] = customer_features["customer_id_nb_tx_14day_window"]
        payload["customer_id_avg_amount_1day_window"] = customer_features["customer_id_avg_amount_1day_window"]
        payload["customer_id_avg_amount_7day_window"] = customer_features["customer_id_avg_amount_7day_window"]
        payload["customer_id_avg_amount_14day_window"] = customer_features["customer_id_avg_amount_14day_window"]
        payload["customer_id_nb_tx_15min_window"] = customer_features["customer_id_nb_tx_15min_window"]
        payload["customer_id_avg_amount_15min_window"] = customer_features["customer_id_avg_amount_15min_window"]
        payload["customer_id_nb_tx_30min_window"] = customer_features["customer_id_nb_tx_30min_window"] 
        payload["customer_id_avg_amount_30min_window"] = customer_features[ "customer_id_avg_amount_30min_window"]
        payload["customer_id_nb_tx_60min_window"] = customer_features["customer_id_nb_tx_60min_window"]
        payload["customer_id_avg_amount_60min_window"] = customer_features["customer_id_avg_amount_60min_window"]
        
        # look up the terminal features from Vertex AI Feature Store
        terminal_features = features_lookup(ff_feature_store, "terminal",[payload_json["TERMINAL_ID"]])
        payload["terminal_id_nb_tx_1day_window"] = terminal_features["terminal_id_nb_tx_1day_window"]
        payload["terminal_id_nb_tx_7day_window"] = terminal_features["terminal_id_nb_tx_7day_window"]
        payload["terminal_id_nb_tx_14day_window"] = terminal_features["terminal_id_nb_tx_14day_window"]
        payload["terminal_id_risk_1day_window"] = terminal_features["terminal_id_risk_1day_window"] 
        payload["terminal_id_risk_7day_window"] = terminal_features["terminal_id_risk_7day_window"]
        payload["terminal_id_risk_14day_window"] = terminal_features["terminal_id_risk_14day_window"]
        payload["terminal_id_nb_tx_15min_window"] = terminal_features["terminal_id_nb_tx_15min_window"]
        payload["terminal_id_avg_amount_15min_window"] = terminal_features["terminal_id_avg_amount_15min_window"]
        payload["terminal_id_nb_tx_30min_window"] = terminal_features["terminal_id_nb_tx_30min_window"]
        payload["terminal_id_avg_amount_30min_window"] = terminal_features["terminal_id_avg_amount_30min_window"]
        payload["terminal_id_nb_tx_60min_window"] = terminal_features["terminal_id_nb_tx_60min_window"]
        payload["terminal_id_avg_amount_60min_window"] = terminal_features["terminal_id_avg_amount_60min_window"]

        payload = preprocess(payload)
        
        print("-------------------------------------------------------")
        print(f"[Pre-processed payload to be sent to Vertex AI endpoint]: {payload}")
        
        result = endpoint_obj.predict(instances = [payload])
        
        print(f"[Prediction result]: {result}")

    return ("", 204)

if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)

