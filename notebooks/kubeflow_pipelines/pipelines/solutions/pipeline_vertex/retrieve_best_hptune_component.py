# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at

# https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
"""Lightweight component tuning function."""
from typing import Dict, List, NamedTuple

from kfp.dsl import component


@component(
    base_image="python:3.8",
    packages_to_install=["google-cloud-aiplatform"],
)
def retrieve_best_hptune_result(
    project: str,
    location: str,
    gcp_resources: str,
    container_uri: str,
    training_file_path: str,
    validation_file_path: str,
) -> NamedTuple(
    "Outputs",
    [
        ("best_parameters", Dict),
        ("best_metrics", Dict),
        ("best_worker_pool_spec", List),
    ],
):

    # pylint: disable=import-outside-toplevel
    import json

    from google.cloud import aiplatform

    aiplatform.init(project=project, location=location)

    # Retrieve the hyperparameter tuning job result
    gcp_resources = json.loads(gcp_resources)
    job_id = gcp_resources["resources"][0]["resourceUri"].split("/")[-1]
    hp_job = aiplatform.HyperparameterTuningJob.get(job_id)

    # Retrieve the best trial
    metrics = [
        trial.final_measurement.metrics[0].value for trial in hp_job.trials
    ]
    goal = hp_job.to_dict()["studySpec"]["metrics"][0]["goal"]
    goal_f = min if goal == "MINIMIZE" else max  # MINIMIZE or MAXIMIZE
    best_result = goal_f(metrics)
    best_trial = hp_job.trials[metrics.index(best_result)]

    best_parameters = {
        param.parameter_id: param.value for param in best_trial.parameters
    }

    best_metrics = {
        m.metric_id: m.value for m in best_trial.final_measurement.metrics
    }

    # Construct worker_pool_spec
    best_worker_pool_spec = [
        {
            "machine_spec": {"machine_type": "n1-standard-4"},
            "replica_count": 1,
            "container_spec": {
                "image_uri": container_uri,
                "args": [
                    f"--training_dataset_path={training_file_path}",
                    f"--validation_dataset_path={validation_file_path}",
                    "--nohptune",
                ],
            },
        }
    ]

    for k, v in best_parameters.items():
        best_worker_pool_spec[0]["container_spec"]["args"].append(f"--{k}={v}")

    return best_parameters, best_metrics, best_worker_pool_spec
