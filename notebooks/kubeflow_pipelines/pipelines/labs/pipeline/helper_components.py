# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
"""Helper components."""

import json
import pickle
import subprocess
import sys
from typing import NamedTuple

import pandas as pd
from sklearn.metrics import accuracy_score, recall_score


def retrieve_best_run(
    project_id: str, job_id: str
) -> NamedTuple(
    "Outputs", [("metric_value", float), ("alpha", float), ("max_iter", int)]
):
    """Retrieves the parameters of the best Hypertune run."""

    # pylint: disable-next=import-outside-toplevel
    from googleapiclient import discovery, errors

    ml = discovery.build("ml", "v1")

    job_name = f"projects/{project_id}/jobs/{job_id}"
    request = ml.projects().jobs().get(name=job_name)

    try:
        response = request.execute()
    except errors.HttpError as err:
        print(err)

    print(response)

    best_trial = response["trainingOutput"]["trials"][0]

    metric_value = best_trial["finalMetric"]["objectiveValue"]
    alpha = float(best_trial["hyperparameters"]["alpha"])
    max_iter = int(best_trial["hyperparameters"]["max_iter"])

    return (metric_value, alpha, max_iter)


def evaluate_model(
    dataset_path: str, model_path: str, metric_name: str
) -> NamedTuple(
    "Outputs",
    [
        ("metric_name", str),
        ("metric_value", float),
        ("mlpipeline_metrics", "Metrics"),
    ],
):
    """Evaluates a trained sklearn model."""

    df_test = pd.read_csv(dataset_path)

    X_test = df_test.drop("Cover_Type", axis=1)  # pylint: disable=invalid-name
    y_test = df_test["Cover_Type"]

    # Copy the model from GCS
    model_filename = "model.pkl"
    gcs_model_filepath = f"{model_path}/{model_filename}"
    print(gcs_model_filepath)
    subprocess.check_call(
        ["gsutil", "cp", gcs_model_filepath, model_filename], stderr=sys.stdout
    )

    with open(model_filename, "rb") as model_file:
        model = pickle.load(model_file)

    y_hat = model.predict(X_test)

    if metric_name == "accuracy":
        metric_value = accuracy_score(y_test, y_hat)
    elif metric_name == "recall":
        metric_value = recall_score(y_test, y_hat)
    else:
        metric_name = "N/A"
        metric_value = 0

    # Export the metric
    metrics = {
        "metrics": [{"name": metric_name, "numberValue": float(metric_value)}]
    }

    return (metric_name, metric_value, json.dumps(metrics))
