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
"""Kubeflow Covertype Pipeline."""
import os

from kfp import dsl
from training_lightweight_component import train_and_deploy
from tuning_lightweight_component import tune_hyperparameters

PIPELINE_ROOT = os.getenv("PIPELINE_ROOT")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

TRAINING_CONTAINER_IMAGE_URI = os.getenv("TRAINING_CONTAINER_IMAGE_URI")
SERVING_CONTAINER_IMAGE_URI = os.getenv("SERVING_CONTAINER_IMAGE_URI")

TRAINING_FILE_PATH = os.getenv("TRAINING_FILE_PATH")
VALIDATION_FILE_PATH = os.getenv("VALIDATION_FILE_PATH")

MAX_TRIAL_COUNT = int(os.getenv("MAX_TRIAL_COUNT", "5"))
PARALLEL_TRIAL_COUNT = int(os.getenv("PARALLEL_TRIAL_COUNT", "5"))
THRESHOLD = float(os.getenv("THRESHOLD", "0.6"))


@dsl.pipeline(
    name="covertype-kfp-pipeline",
    description="The pipeline training and deploying the Covertype classifier",
    pipeline_root=PIPELINE_ROOT,
)
def covertype_train(
    training_container_uri: str = TRAINING_CONTAINER_IMAGE_URI,
    serving_container_uri: str = SERVING_CONTAINER_IMAGE_URI,
    training_file_path: str = TRAINING_FILE_PATH,
    validation_file_path: str = VALIDATION_FILE_PATH,
    accuracy_deployment_threshold: float = THRESHOLD,
    max_trial_count: int = MAX_TRIAL_COUNT,
    parallel_trial_count: int = PARALLEL_TRIAL_COUNT,
    pipeline_root: str = PIPELINE_ROOT,
):
    staging_bucket = f"{pipeline_root}/staging"

    tuning_op = tune_hyperparameters(
        project=PROJECT_ID,
        location=REGION,
        container_uri=training_container_uri,
        training_file_path=training_file_path,
        validation_file_path=validation_file_path,
        staging_bucket=staging_bucket,
        max_trial_count=max_trial_count,
        parallel_trial_count=parallel_trial_count,
    )

    accuracy = tuning_op.outputs["best_accuracy"]

    with dsl.Condition(
        accuracy >= accuracy_deployment_threshold, name="deploy_decision"
    ):
        train_and_deploy_op = (  # pylint: disable=unused-variable
            train_and_deploy(
                project=PROJECT_ID,
                location=REGION,
                container_uri=training_container_uri,
                serving_container_uri=serving_container_uri,
                training_file_path=training_file_path,
                validation_file_path=validation_file_path,
                staging_bucket=staging_bucket,
                alpha=tuning_op.outputs["best_alpha"],
                max_iter=tuning_op.outputs["best_max_iter"],
            )
        )
