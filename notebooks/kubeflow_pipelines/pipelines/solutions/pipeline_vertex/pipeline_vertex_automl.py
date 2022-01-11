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

from google_cloud_pipeline_components.aiplatform import (
    AutoMLTabularTrainingJobRunOp,
    EndpointCreateOp,
    ModelDeployOp,
    TabularDatasetCreateOp,
)
from kfp.v2 import dsl

PIPELINE_ROOT = os.getenv("PIPELINE_ROOT")
PROJECT = os.getenv("PROJECT")
DATASET_SOURCE = os.getenv("DATASET_SOURCE")
PIPELINE_NAME = os.getenv("PIPELINE_NAME", "covertype")
DISPLAY_NAME = os.getenv("MODEL_DISPLAY_NAME", PIPELINE_NAME)
TARGET_COLUMN = os.getenv("TARGET_COLUMN", "Cover_Type")
SERVING_MACHINE_TYPE = os.getenv("SERVING_MACHINE_TYPE", "n1-standard-16")


@dsl.pipeline(
    name=f"{PIPELINE_NAME}-vertex-automl-pipeline",
    description=f"AutoML Vertex Pipeline for {PIPELINE_NAME}",
    pipeline_root=PIPELINE_ROOT,
)
def create_pipeline():

    dataset_create_task = TabularDatasetCreateOp(
        display_name=DISPLAY_NAME,
        bq_source=DATASET_SOURCE,
        project=PROJECT,
    )

    automl_training_task = AutoMLTabularTrainingJobRunOp(
        project=PROJECT,
        display_name=DISPLAY_NAME,
        optimization_prediction_type="classification",
        dataset=dataset_create_task.outputs["dataset"],
        target_column=TARGET_COLUMN,
    )

    endpoint_create_task = EndpointCreateOp(
        project=PROJECT,
        display_name=DISPLAY_NAME,
    )

    model_deploy_task = ModelDeployOp(  # pylint: disable=unused-variable
        model=automl_training_task.outputs["model"],
        endpoint=endpoint_create_task.outputs["endpoint"],
        deployed_model_display_name=DISPLAY_NAME,
        dedicated_resources_machine_type=SERVING_MACHINE_TYPE,
        dedicated_resources_min_replica_count=1,
        dedicated_resources_max_replica_count=1,
    )
