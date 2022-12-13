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

from google.cloud.aiplatform import hyperparameter_tuning as hpt
from google_cloud_pipeline_components.aiplatform import (
    EndpointCreateOp,
    ModelDeployOp,
    ModelUploadOp,
)
from google_cloud_pipeline_components.experimental import (
    hyperparameter_tuning_job,
)
from google_cloud_pipeline_components.experimental.custom_job import (
    CustomTrainingJobOp,
)
from kfp.v2 import dsl

PIPELINE_ROOT = os.getenv("PIPELINE_ROOT")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION")

TRAINING_CONTAINER_IMAGE_URI = os.getenv("TRAINING_CONTAINER_IMAGE_URI")
SERVING_CONTAINER_IMAGE_URI = os.getenv("SERVING_CONTAINER_IMAGE_URI")
SERVING_MACHINE_TYPE = os.getenv("SERVING_MACHINE_TYPE", "n1-standard-16")

TRAINING_FILE_PATH = os.getenv("TRAINING_FILE_PATH")
VALIDATION_FILE_PATH = os.getenv("VALIDATION_FILE_PATH")

MAX_TRIAL_COUNT = int(os.getenv("MAX_TRIAL_COUNT", "5"))
PARALLEL_TRIAL_COUNT = int(os.getenv("PARALLEL_TRIAL_COUNT", "5"))
THRESHOLD = float(os.getenv("THRESHOLD", "0.6"))

PIPELINE_NAME = os.getenv("PIPELINE_NAME", "covertype")
BASE_OUTPUT_DIR = os.getenv("BASE_OUTPUT_DIR", PIPELINE_ROOT)
MODEL_DISPLAY_NAME = os.getenv("MODEL_DISPLAY_NAME", PIPELINE_NAME)


@dsl.pipeline(
    name=f"{PIPELINE_NAME}-kfp-pipeline",
    description="Kubeflow pipeline that tunes, trains, and deploys on Vertex",
    pipeline_root=PIPELINE_ROOT,
)
def create_pipeline():

    worker_pool_specs = [
        {
            "machine_spec": {
                "machine_type": "n1-standard-4",
                "accelerator_type": "NVIDIA_TESLA_T4",
                "accelerator_count": 1,
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": TRAINING_CONTAINER_IMAGE_URI,
                "args": [
                    f"--training_dataset_path={TRAINING_FILE_PATH}",
                    f"--validation_dataset_path={VALIDATION_FILE_PATH}",
                    "--hptune",
                ],
            },
        }
    ]

    metric_spec = hyperparameter_tuning_job.serialize_metrics(
        {"accuracy": "maximize"}
    )

    parameter_spec = hyperparameter_tuning_job.serialize_parameters(
        {
            "alpha": hpt.DoubleParameterSpec(
                min=1.0e-4, max=1.0e-1, scale="linear"
            ),
            "max_iter": hpt.DiscreteParameterSpec(
                values=[1, 2], scale="linear"
            ),
        }
    )

    hp_tuning_task = hyperparameter_tuning_job.HyperparameterTuningJobRunOp(
        display_name=f"{PIPELINE_NAME}-kfp-tuning-job",
        project=PROJECT_ID,
        location=REGION,
        worker_pool_specs=worker_pool_specs,
        study_spec_metrics=metric_spec,
        study_spec_parameters=parameter_spec,
        max_trial_count=MAX_TRIAL_COUNT,
        parallel_trial_count=PARALLEL_TRIAL_COUNT,
        base_output_directory=PIPELINE_ROOT,
    )

    trials_task = hyperparameter_tuning_job.GetTrialsOp(
        gcp_resources=hp_tuning_task.outputs["gcp_resources"]
    )

    best_hyperparameters_task = (
        hyperparameter_tuning_job.GetBestHyperparametersOp(
            trials=trials_task.output, study_spec_metrics=metric_spec
        )
    )

    # Construct new worker_pool_specs and
    # train new model based on best hyperparameters
    worker_pool_specs_task = hyperparameter_tuning_job.GetWorkerPoolSpecsOp(
        best_hyperparameters=best_hyperparameters_task.output,
        worker_pool_specs=[
            {
                "machine_spec": {"machine_type": "n1-standard-4"},
                "replica_count": 1,
                "container_spec": {
                    "image_uri": TRAINING_CONTAINER_IMAGE_URI,
                    "args": [
                        f"--training_dataset_path={TRAINING_FILE_PATH}",
                        f"--validation_dataset_path={VALIDATION_FILE_PATH}",
                        "--nohptune",
                    ],
                },
            }
        ],
    )

    training_task = CustomTrainingJobOp(
        project=PROJECT_ID,
        location=REGION,
        display_name=f"{PIPELINE_NAME}-kfp-training-job",
        worker_pool_specs=worker_pool_specs_task.output,
        base_output_directory=BASE_OUTPUT_DIR,
    )

    model_upload_task = ModelUploadOp(
        project=PROJECT_ID,
        display_name=f"{PIPELINE_NAME}-kfp-model-upload-job",
        artifact_uri=f"{BASE_OUTPUT_DIR}/model",
        serving_container_image_uri=SERVING_CONTAINER_IMAGE_URI,
    )
    model_upload_task.after(training_task)

    endpoint_create_task = EndpointCreateOp(
        project=PROJECT_ID,
        display_name=f"{PIPELINE_NAME}-kfp-create-endpoint-job",
    )
    endpoint_create_task.after(model_upload_task)

    model_deploy_op = ModelDeployOp(  # pylint: disable=unused-variable
        model=model_upload_task.outputs["model"],
        endpoint=endpoint_create_task.outputs["endpoint"],
        deployed_model_display_name=MODEL_DISPLAY_NAME,
        dedicated_resources_machine_type=SERVING_MACHINE_TYPE,
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1,
    )
