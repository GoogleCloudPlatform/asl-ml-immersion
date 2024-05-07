# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at

# https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
"""Compute and log classification metrics."""

from google_cloud_pipeline_components.types.artifact_types import BQTable
from kfp.dsl import ClassificationMetrics, Input, Output, component


@component(
    base_image="us-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0:latest",
    packages_to_install=[
        "google-cloud-pipeline-components==2.8.0",
        "google-cloud-bigquery",
        "db-dtypes",
    ],
)
def compute_cls_metrics(
    batch_pred_result: Input[BQTable],
    class_names: list,
    label_column: str,
    cls_metrics: Output[ClassificationMetrics],
    prediction_column: str = "prediction",
):
    from google.cloud import bigquery  # pylint: disable=import-outside-toplevel
    from sklearn.metrics import (  # pylint: disable=import-outside-toplevel
        confusion_matrix,
    )

    client = bigquery.Client(batch_pred_result.metadata["projectId"])

    query = (
        f"SELECT {label_column}, {prediction_column} FROM "
        f"{batch_pred_result.metadata['datasetId']}."  # pylint: disable=inconsistent-quotes
        f"{batch_pred_result.metadata['tableId']}"  # pylint: disable=inconsistent-quotes
    )

    result = client.query(query).to_dataframe()
    label = result[label_column].astype(int)
    prediction = result[prediction_column].astype(int)

    cls_metrics.log_confusion_matrix(
        class_names, confusion_matrix(label, prediction).tolist()
    )
