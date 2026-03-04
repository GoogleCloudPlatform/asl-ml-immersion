#!/bin/bash
# Copyright 2026 Google LLC. All Rights Reserved.
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

# ==============================================================================
# CONFIGURATION VARIABLES
# ==============================================================================
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
ZONE="us-central1-a"
INSTANCE_NAME="asl-lab-workbench"
MACHINE_TYPE="e2-standard-4"

if [ "$ENABLE_GPU" == "true" ]; then
    INSTANCE_NAME="${INSTANCE_NAME}-gpu"
    MACHINE_TYPE="n1-standard-4"
fi

# ==============================================================================
# PRE-FLIGHT CHECKS
# ==============================================================================

if [ -z "$PROJECT_ID" ]; then
  echo "Error: No Google Cloud Project set. Please run 'gcloud config set project <PROJECT_ID>' first."
  exit 1
fi

echo "🚀 Starting Workbench setup for Project: $PROJECT_ID in Zone: $ZONE"

# 1. Enable Notebooks API
echo "----------------------------------------------------------------"
echo "Step 1: Enabling Notebooks API..."
gcloud services enable notebooks.googleapis.com
echo "API Enabled."

# 2. Create Workbench Instance
echo "----------------------------------------------------------------"
echo "Step 2: Checking/Creating Workbench Instance '$INSTANCE_NAME'..."

if gcloud workbench instances describe $INSTANCE_NAME --location=$ZONE --project=$PROJECT_ID > /dev/null 2>&1; then
    echo "Instance '$INSTANCE_NAME' already exists. Skipping creation."
else
    echo "Creating instance... (This takes a few minutes)"

    GPU_ARGS=""
    if [ "$ENABLE_GPU" == "true" ]; then
        GPU_ARGS="--accelerator-type=NVIDIA_TESLA_T4 --accelerator-core-count=1 --install-gpu-driver"
    fi

    if gcloud workbench instances create $INSTANCE_NAME \
        --project=$PROJECT_ID \
        --machine-type=$MACHINE_TYPE \
        --location=$ZONE \
        --network="projects/${PROJECT_ID}/global/networks/default" \
        --subnet="projects/${PROJECT_ID}/regions/${REGION}/subnetworks/default" \
        --metadata=idle-timeout-seconds= \
        $GPU_ARGS; then
        echo "Instance created."
    else
        echo "Error: Failed to create Workbench instance."
        exit 1
    fi
fi

echo "================================================================"
echo "✅ Workbench '$INSTANCE_NAME' is ready!"
echo "   Link: https://console.cloud.google.com/vertex-ai/workbench/instances?project=$PROJECT_ID"
echo "================================================================"
