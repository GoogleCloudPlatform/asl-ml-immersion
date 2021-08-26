# Lint as: python2, python3
# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TFX taxi template configurations.

This file defines environments for a TFX taxi pipeline.
"""

import os  # pylint: disable=unused-import

# TODO(b/149347293): Move more TFX CLI flags into python configuration.

# Pipeline name will be used to identify this pipeline.
PIPELINE_NAME = 'guided_project_2_solution'

# GCP related configs.

# Following code will retrieve your GCP project. You can choose which project
# to use by setting GOOGLE_CLOUD_PROJECT environment variable.
try:
  import google.auth  # pylint: disable=g-import-not-at-top
  try:
    _, GOOGLE_CLOUD_PROJECT = google.auth.default()
  except google.auth.exceptions.DefaultCredentialsError:
    GOOGLE_CLOUD_PROJECT = ''
except ImportError:
  GOOGLE_CLOUD_PROJECT = ''

# Specify your GCS bucket name here. You have to use GCS to store output files
# when running a pipeline with Kubeflow Pipeline on GCP or when running a job
# using Dataflow. Default is '<gcp_project_name>-kubeflowpipelines-default'.
# This bucket is created automatically when you deploy KFP from marketplace.
GCS_BUCKET_NAME = GOOGLE_CLOUD_PROJECT + '-kubeflowpipelines-default'

# TODO(step 8,step 9): (Optional) Set your region to use GCP services including
#                      BigQuery, Dataflow and Cloud AI Platform.
GOOGLE_CLOUD_REGION = 'us-central1'

PREPROCESSING_FN = 'models.preprocessing.preprocessing_fn'
RUN_FN = 'models.keras.model.run_fn'
# NOTE: Uncomment below to use an estimator based model.
# RUN_FN = 'models.estimator.model.run_fn'

TRAIN_NUM_STEPS = 5000
EVAL_NUM_STEPS = 500

# Change this value according to your use cases.
EVAL_ACCURACY_THRESHOLD = 0.6

# Beam args to use BigQueryExampleGen with Beam DirectRunner.
# TODO(step 7): (Optional) Uncomment here to provide GCP related configs for
#               BigQuery.
# BIG_QUERY_WITH_DIRECT_RUNNER_BEAM_PIPELINE_ARGS = [
#    '--project=' + GOOGLE_CLOUD_PROJECT,
#    '--temp_location=' + os.path.join('gs://', GCS_BUCKET_NAME, 'tmp'),
#    ]

# The rate at which to sample rows from the Chicago Taxi dataset using BigQuery.
# The full taxi dataset is > 120M record.  In the interest of resource
# savings and time, we've set the default for this example to be much smaller.
# Feel free to crank it up and process the full dataset!
_query_sample_rate = 0.0001  # Generate a 0.01% random sample.

# The query that extracts the examples from BigQuery.  The Chicago Taxi dataset
# used for this example is a public dataset available on Google AI Platform.
# https://console.cloud.google.com/marketplace/details/city-of-chicago-public-data/chicago-taxi-trips
# TODO(step 7): (Optional) Uncomment here to use BigQuery.
# BIG_QUERY_QUERY = """
#         SELECT
#           pickup_community_area,
#           fare,
#           EXTRACT(MONTH FROM trip_start_timestamp) AS trip_start_month,
#           EXTRACT(HOUR FROM trip_start_timestamp) AS trip_start_hour,
#           EXTRACT(DAYOFWEEK FROM trip_start_timestamp) AS trip_start_day,
#           UNIX_SECONDS(trip_start_timestamp) AS trip_start_timestamp,
#           pickup_latitude,
#           pickup_longitude,
#           dropoff_latitude,
#           dropoff_longitude,
#           trip_miles,
#           pickup_census_tract,
#           dropoff_census_tract,
#           payment_type,
#           company,
#           trip_seconds,
#           dropoff_community_area,
#           tips,
#           IF(tips > fare * 0.2, 1, 0) AS big_tipper
#         FROM `bigquery-public-data.chicago_taxi_trips.taxi_trips`
#         WHERE (ABS(FARM_FINGERPRINT(unique_key)) / 0x7FFFFFFFFFFFFFFF)
#           < {query_sample_rate}""".format(
#    query_sample_rate=_query_sample_rate)

# Beam args to run data processing on DataflowRunner.
#
# TODO(b/151114974): Remove `disk_size_gb` flag after default is increased.
# TODO(b/151116587): Remove `shuffle_mode` flag after default is changed.
# TODO(b/156874687): Remove `machine_type` after IP addresses are no longer a
#                    scaling bottleneck.
# TODO(step 8): (Optional) Uncomment below to use Dataflow.
# DATAFLOW_BEAM_PIPELINE_ARGS = [
#    '--project=' + GOOGLE_CLOUD_PROJECT,
#    '--runner=DataflowRunner',
#    '--temp_location=' + os.path.join('gs://', GCS_BUCKET_NAME, 'tmp'),
#    '--region=' + GOOGLE_CLOUD_REGION,
#
#    # Temporary overrides of defaults.
#    '--disk_size_gb=50',
#    '--experiments=shuffle_mode=auto',
#    '--machine_type=n1-standard-8',
#    ]

# A dict which contains the training job parameters to be passed to Google
# Cloud AI Platform. For the full set of parameters supported by Google Cloud AI
# Platform, refer to
# https://cloud.google.com/ml-engine/reference/rest/v1/projects.jobs#Job
# TODO(step 9): (Optional) Uncomment below to use AI Platform training.
GCP_AI_PLATFORM_TRAINING_ARGS = {
    'project': GOOGLE_CLOUD_PROJECT,
    'region': GOOGLE_CLOUD_REGION,
    # Starting from TFX 0.14, training on AI Platform uses custom containers:
    # https://cloud.google.com/ml-engine/docs/containers-overview
    # You can specify a custom container here. If not specified, TFX will use
    # a public container image matching the installed version of TFX.
    # TODO(step 9): (Optional) Set your container name below.
    'masterConfig': {
      'imageUri': 'gcr.io/' + GOOGLE_CLOUD_PROJECT + '/tfx-pipeline'
    },
    # Note that if you do specify a custom container, ensure the entrypoint
    # calls into TFX's run_executor script (tfx/scripts/run_executor.py)
}

# A dict which contains the serving job parameters to be passed to Google
# Cloud AI Platform. For the full set of parameters supported by Google Cloud AI
# Platform, refer to
# https://cloud.google.com/ml-engine/reference/rest/v1/projects.models
# TODO(step 9): (Optional) Uncomment below to use AI Platform serving.
GCP_AI_PLATFORM_SERVING_ARGS = {
    'model_name': PIPELINE_NAME.replace('-','_'),  # '-' is not allowed.
    'project_id': GOOGLE_CLOUD_PROJECT,
    # The region to use when serving the model. See available regions here:
    # https://cloud.google.com/ml-engine/docs/regions
    # Note that serving currently only supports a single region:
    # https://cloud.google.com/ml-engine/reference/rest/v1/projects.models#Model  # pylint: disable=line-too-long
    'regions': [GOOGLE_CLOUD_REGION],
}
