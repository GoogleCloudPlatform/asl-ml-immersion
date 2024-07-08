#!/bin/bash
# Copyright 2023 Google LLC. All Rights Reserved.
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

# Configure variables
echo 'export PATH=$PATH:~/.local/bin:' >> ~/.bash_profile
echo 'export PATH=$PATH:~/.local/bin:' >> ~/.bashrc

# Enable Google Cloud services
gcloud services enable \
  compute.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com \
  monitoring.googleapis.com \
  logging.googleapis.com \
  notebooks.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  container.googleapis.com \
  dataflow.googleapis.com

# Setup Artifact Registry
export PROJECT_ID=$(gcloud config get-value project)
export BUCKET=$PROJECT_ID
export MULTIREGION=us
export REGION=us-central1
export ARTIFACT_REG_REPO=asl-artifact-repo

if ! gcloud artifacts repositories describe $ARTIFACT_REG_REPO \
       --location=$MULTIREGION > /dev/null 2>&1; then
    gcloud artifacts repositories create $ARTIFACT_REG_REPO \
    --project=$PROJECT_ID --location=$MULTIREGION --repository-format=docker
fi

# Create a GCS bucket
exists=$(gsutil ls -d | grep -w gs://${BUCKET}/)
if [ -n "$exists" ]; then
    echo -e "Bucket exists, let's not recreate it."
else
    echo "Creating a new GCS bucket."
    gsutil mb -l ${REGION} gs://${BUCKET}
    echo "Here are your current buckets:"
    gsutil ls
fi
