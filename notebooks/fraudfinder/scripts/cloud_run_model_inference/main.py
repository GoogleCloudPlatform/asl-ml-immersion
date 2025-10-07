# pylint: skip-file
# Copyright 2025 Google, LLC.
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
import json
import os

from flask import Flask, request
from google.cloud import aiplatform as aiplatform
from google.cloud import pubsub_v1


# General imports
import os
import random
import sys
from datetime import datetime, timedelta

# from google.cloud import aiplatform
from google.cloud import aiplatform as vertex_ai
from google.cloud import bigquery
from google.cloud.aiplatform_v1 import (
    FeatureOnlineStoreAdminServiceClient,
    FeatureOnlineStoreServiceClient,
    FeatureRegistryServiceClient,
)
from google.cloud.aiplatform_v1.types import feature as feature_pb2
from google.cloud.aiplatform_v1.types import feature_group as feature_group_pb2
from google.cloud.aiplatform_v1.types import (
    feature_online_store as feature_online_store_pb2,
)
from google.cloud.aiplatform_v1.types import (
    feature_online_store_admin_service as feature_online_store_admin_service_pb2,
)
from google.cloud.aiplatform_v1.types import (
    feature_online_store_service as feature_online_store_service_pb2,
)
from google.cloud.aiplatform_v1.types import (
    feature_registry_service as feature_registry_service_pb2,
)
from google.cloud.aiplatform_v1.types import feature_view as feature_view_pb2
from google.cloud.aiplatform_v1.types import (
    featurestore_service as featurestore_service_pb2,
)
from google.cloud.aiplatform_v1.types import io as io_pb2

# Retrieve environment variables
PROJECT_ID = os.environ.get("PROJECT_ID", "PROJECT_ID variable is not set.")
ENDPOINT_ID = os.environ.get("ENDPOINT_ID", "ENDPOINT_ID variable is not set.")
FEATURESTORE_ID = os.environ.get(
    "FEATURESTORE_ID", "FEATURESTORE_ID variable is not set."
)
REGION = os.environ.get("REGION", "REGION variable is not set.")


app = Flask(__name__)

# Instantiate Vertex AI Feature Store object
try:
    API_ENDPOINT = f"{REGION}-aiplatform.googleapis.com"

    # Instantiate Vertex AI Feature Store object

    data_client = FeatureOnlineStoreServiceClient(
        client_options={"api_endpoint": API_ENDPOINT}
    )

except NameError:
    print(f"""The feature store {FEATURESTORE_ID} does not exist!""")

# Instantiate the Vertex AI endpoint object
aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint_obj = aiplatform.Endpoint(ENDPOINT_ID)


def fs_features_lookup(ff_feature_store, features_type, features_key):

    FEATURE_VIEW_ID = f"fv_fraudfinder_{features_type}"
    FEATURE_VIEW_FULL_ID = f"projects/{PROJECT_ID}/locations/{REGION}/featureOnlineStores/{ff_feature_store}/featureViews/{FEATURE_VIEW_ID}"

    features_map = {}

    print(FEATURE_VIEW_FULL_ID)

    try:
        fe_continuous_data = data_client.fetch_feature_values(
            request=feature_online_store_service_pb2.FetchFeatureValuesRequest(
                feature_view=FEATURE_VIEW_FULL_ID,
                data_key=feature_online_store_service_pb2.FeatureViewDataKey(
                    key=features_key
                ),
                data_format=feature_online_store_service_pb2.FeatureViewDataFormat.PROTO_STRUCT,
            )
        )
        features_map.update({k: v for k, v in fe_continuous_data.proto_struct.items()})
    except Exception as exp:
        print(f"Requested entity {features_key} was not found")
    return features_map


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

        default_features = {
            "customer_id_avg_amount_14day_window": 0,
            "customer_id_avg_amount_15min_window": 0,
            "customer_id_avg_amount_1day_window": 0,
            "customer_id_avg_amount_30min_window": 0,
            "customer_id_avg_amount_60min_window": 0,
            "customer_id_avg_amount_7day_window": 0,
            "customer_id_nb_tx_14day_window": 0,
            "customer_id_nb_tx_7day_window": 0,
            "customer_id_nb_tx_15min_window": 0,
            "customer_id_nb_tx_1day_window": 0,
            "customer_id_nb_tx_30min_window": 0,
            "customer_id_nb_tx_60min_window": 0,
            "terminal_id_avg_amount_15min_window": 0,
            "terminal_id_avg_amount_30min_window": 0,
            "terminal_id_avg_amount_60min_window": 0,
            "terminal_id_nb_tx_14day_window": 0,
            "terminal_id_nb_tx_15min_window": 0,
            "terminal_id_nb_tx_1day_window": 0,
            "terminal_id_nb_tx_30min_window": 0,
            "terminal_id_nb_tx_60min_window": 0,
            "terminal_id_nb_tx_7day_window": 0,
            "terminal_id_risk_14day_window": 0,
            "terminal_id_risk_1day_window": 0,
            "terminal_id_risk_7day_window": 0,
        }

        payload = default_features
        payload["tx_amount"] = payload_json["TX_AMOUNT"]

        # look up the customer features from New Vertex AI Feature Store
        customer_features = fs_features_lookup(
            FEATURESTORE_ID, "customers", payload_json["CUSTOMER_ID"]
        )
        # print the customer features from Vertex AI Feature Store
        print("-------------------------------------------------------")
        print("customer_features:")
        print(customer_features)

        # look up the treminal features from New Vertex AI Feature Store
        terminal_features = fs_features_lookup(
            FEATURESTORE_ID, "terminals", payload_json["TERMINAL_ID"]
        )
        print("-------------------------------------------------------")
        print("terminal features:")
        print(terminal_features)

        # Add customer features to payload
        payload.update(customer_features)

        # Add terminal features to payload
        payload.update(terminal_features)

        # del payload["feature_timestamp"]

        print("-------------------------------------------------------")
        print("[Payload to be sent to Vertex AI endpoint]")
        print(payload)
        print("-------------------------------------------------------")

        result = endpoint_obj.predict(instances=[payload])

        print("-------------------------------------------------------")
        print(f"[Prediction result]: {result}")
        print("-------------------------------------------------------")

    return ("", 204)


if __name__ == "__main__":
    PORT = int(os.getenv("PORT")) if os.getenv("PORT") else 8080

    # This is used when running locally. Gunicorn is used to run the
    # application on Cloud Run. See entrypoint in Dockerfile.
    app.run(host="127.0.0.1", port=PORT, debug=True)
