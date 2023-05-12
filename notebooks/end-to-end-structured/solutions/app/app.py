import json
import os

from flask import Flask
from flask import jsonify
from flask import render_template
from flask import request

from google.cloud import aiplatform


# Set the environment variables before launching the app
PROJECT_ID = os.getenv("PROJECT_ID")
ENDPOINT_ID = os.getenv("ENDPOINT_ID")
LOCATION = os.getenv("LOCATION", "us-central1")
API_ENDPOINT = os.getenv("API_ENDPOINT", "us-central1-aiplatform.googleapis.com")

msg = "Set the PROJECT_ID and ENDOPOINT_ID in the environment first."
assert PROJECT_ID, msg
assert ENDPOINT_ID, msg

app = Flask(__name__)


def get_prediction(instance):
    client = aiplatform.gapic.PredictionServiceClient(
        client_options={"api_endpoint": API_ENDPOINT})
    endpoint = client.endpoint_path(
        project=PROJECT_ID, location=LOCATION, endpoint=ENDPOINT_ID
    )
    response = client.predict(endpoint=endpoint, instances=[instance])
    predictions = response.predictions
    return predictions[0][0]


def get_gender(data):
    value = data["baby_gender"]
    genders = {"unknown": "Unknown", "male": "True", "female": "False"}
    return [genders[value]]


def get_plurality(data):
    value = data["plurality"]
    pluralities = {"1": "Single(1)", "2": "Twins(2)", "3": "Triplets(3)"}
    if data["baby_gender"] == "unknown" and int(value) > 1:
        return ["Multiple(2+)"]
    return [pluralities[value]]


def get_mother_age(data):
    return [float(data["mother_age"])]


def get_gestation_weeks(data):
    return [float(data["gestation_weeks"])]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/predict", methods=["POST"])
def predict():

    data = json.loads(request.data.decode())
    mandatory_items = ["baby_gender",
                       "mother_age",
                       "plurality",
                       "gestation_weeks"]
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

    return jsonify({"result": "{:.2f} lbs.".format(prediction)})
