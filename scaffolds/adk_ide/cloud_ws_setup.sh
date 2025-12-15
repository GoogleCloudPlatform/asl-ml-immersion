#!/bin/bash

# ==============================================================================
# CONFIGURATION VARIABLES
# Change these values as needed to suit your environment.
# ==============================================================================
PROJECT_ID=$(gcloud config get-value project)
REGION="us-central1"
CLUSTER_NAME="asl-lab-cluster"
CONFIG_NAME="asl-lab-code-oss-config"
WORKSTATION_NAME="asl-lab-workstation"

# The network/subnet where the cluster will live.
# Ensure Private Google Access is enabled on this subnet.
NETWORK="default"
SUBNET="default"

# ==============================================================================
# PRE-FLIGHT CHECKS
# ==============================================================================

if [ -z "$PROJECT_ID" ]; then
  echo "Error: No Google Cloud Project set. Please run 'gcloud config set project <PROJECT_ID>' first."
  exit 1
fi

echo "🚀 Starting setup for Project: $PROJECT_ID in Region: $REGION"

# 1. Enable Cloud Workstations API
echo "----------------------------------------------------------------"
echo "Step 1: Enabling Cloud Workstations API..."
gcloud services enable workstations.googleapis.com
echo "API Enabled."

# 2. Get Project Number to construct the Default Service Account email
echo "----------------------------------------------------------------"
echo "Step 2: Retrieving Default Compute Service Account..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
DEFAULT_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

echo "Targeting Service Account: $DEFAULT_SA"

# ==============================================================================
# INFRASTRUCTURE CREATION
# ==============================================================================

# 3. Create Workstation Cluster
echo "----------------------------------------------------------------"
echo "Step 3: Checking/Creating Workstation Cluster '$CLUSTER_NAME'..."

if gcloud workstations clusters describe $CLUSTER_NAME --region=$REGION > /dev/null 2>&1; then
    echo "Cluster '$CLUSTER_NAME' already exists. Skipping creation."
else
    echo "Creating cluster... (This takes ~20 minutes)"
    gcloud workstations clusters create $CLUSTER_NAME \
        --region=$REGION \
        --network=$FULL_NETWORK_PATH \
        --subnetwork=$FULL_SUBNET_PATH \
        --quiet
fi

# Wait for cluster to be ready
echo "Waiting for cluster to be in READY state..."
while [[ $(gcloud workstations clusters describe $CLUSTER_NAME --region=$REGION --format="value(reconciling)") == "true" ]]; do
    sleep 10
    echo -n "."
done
echo " Cluster is Ready."

# 4. Create Workstation Configuration
# This defines the "Default IDE" (Code OSS) and attaches the Default SA.
echo "----------------------------------------------------------------"
echo "Step 4: Creating Workstation Configuration '$CONFIG_NAME'..."

# The image URI for the default Code OSS (VS Code) IDE.
# We use the variable region to ensure we pull from the correct registry location.
IMAGE_URI="$REGION-docker.pkg.dev/cloud-workstations-images/predefined/code-oss:latest"

if gcloud workstations configs describe $CONFIG_NAME --region=$REGION --cluster=$CLUSTER_NAME > /dev/null 2>&1; then
    echo "Configuration '$CONFIG_NAME' already exists. Skipping."
else
    gcloud workstations configs create $CONFIG_NAME \
        --region=$REGION \
        --cluster=$CLUSTER_NAME \
        --machine-type="e2-standard-4" \
        --container-image="$IMAGE_URI" \
        --service-account="$DEFAULT_SA" \
        --service-account-scopes="https://www.googleapis.com/auth/cloud-platform" \
        --quiet
    echo "Configuration created with Service Account: $DEFAULT_SA"
fi

# 5. Create the Workstation Instance
echo "----------------------------------------------------------------"
echo "Step 5: Creating Workstation Instance '$WORKSTATION_NAME'..."

if gcloud workstations describe $WORKSTATION_NAME --region=$REGION --cluster=$CLUSTER_NAME --config=$CONFIG_NAME > /dev/null 2>&1; then
    echo "Workstation '$WORKSTATION_NAME' already exists."
else
    gcloud workstations create $WORKSTATION_NAME \
        --region=$REGION \
        --cluster=$CLUSTER_NAME \
        --config=$CONFIG_NAME \
        --quiet
    echo "Workstation created."
fi

# 6. Start the Workstation
echo "----------------------------------------------------------------"
echo "Step 6: Spinning up (Starting) the Workstation..."
gcloud workstations start $WORKSTATION_NAME \
    --region=$REGION \
    --cluster=$CLUSTER_NAME \
    --config=$CONFIG_NAME

echo "================================================================"
echo "✅ Workstation '$WORKSTATION_NAME' is running!"
echo "   IDE: Code OSS (Default)"
echo "   Service Account: $DEFAULT_SA"
echo ""
echo "To launch the IDE in your browser, use the link in the Console or run:"
echo "   gcloud workstations start-tcp-tunnel $WORKSTATION_NAME \\"
echo "     --region=$REGION --cluster=$CLUSTER_NAME --config=$CONFIG_NAME \\"
echo "     --local-host-port=:8080 80"
echo "================================================================"