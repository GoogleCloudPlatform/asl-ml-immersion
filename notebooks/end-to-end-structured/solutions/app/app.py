"""Simple webapp illustrating how to query a Vertex model.
"""

import json
import os

from flask import Flask, jsonify, render_template, request
from google.cloud import aiplatform

# Set the environment variables before launching the app
PROJECT_ID = os.getenv("PROJECT_ID")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
API_ENDPOINT = os.getenv(
    "API_ENDPOINT", "us-central1-aiplatform.googleapis.com"
)

msg = "Set the PROJECT_ID and ENDOPOINT_ID in the environment first."
assert PROJECT_ID, msg
assert ENDPOINT_ID, msg

app = Flask(__name__)


def get_prediction(instance):
    """Retrieve predictions from the deployed model."""
    client = aiplatform.gapic.PredictionServiceClient(
        client_options={"api_endpoint": API_ENDPOINT}
    )
    endpoint = client.endpoint_path(
        project=PROJECT_ID, location=LOCATION, endpoint=ENDPOINT_ID
    )
    response = client.predict(endpoint=endpoint, instances=[instance])
    predictions = response.predictions
    return predictions[0][0]


def get_gender(data):
    """Extract gender data from the request."""
    value = data["baby_gender"]
    genders = {"unknown": "Unknown", "male": "True", "female": "False"}
    return [genders[value]]


def get_plurality(data):
    """Extract plurality data from the request."""
    value = data["plurality"]
    pluralities = {"1": "Single(1)", "2": "Twins(2)", "3": "Triplets(3)"}
    if data["baby_gender"] == "unknown" and int(value) > 1:
        return ["Multiple(2+)"]
    return [pluralities[value]]


def get_mother_age(data):
    """Extract age data from the request."""
    return [float(data["mother_age"])]


def get_gestation_weeks(data):
    """Extract gestation duration data from the request."""
    return [float(data["gestation_weeks"])]


@app.route("/")
def index():
    """Index route."""
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    """Predict route."""
    data = json.loads(request.data.decode())
    mandatory_items = [
        "baby_gender",
        "mother_age",
        "plurality",
        "gestation_weeks",
    ]
    for item in mandatory_items:
        if item not in data.keys():
            return jsonify({"result": "Set all items."})

    instance = {
        "is_male": get_gender(data),
        "mother_age": get_mother_age(data),
        "plurality": get_plurality(data),
        "gestation_weeks": get_gestation_weeks(data),
    }

    prediction = get_prediction(instance)

    return jsonify({"result": f"{prediction:.2f} lbs."})
