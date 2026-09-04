#!/bin/bash

# POSIX-compliant way to resolve the directory of this script,
# ensuring compatibility when run with either 'sh' or 'bash'.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

export PATH=$PATH:~/.local/bin
echo "Executing from directory: $(pwd)"

# Robustly load and export variables from .env if it exists
if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

# Fallback defaults if not set in environment or .env
GOOGLE_CLOUD_PROJECT="${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}"
GOOGLE_CLOUD_LOCATION="${GOOGLE_CLOUD_LOCATION:-us-central1}"

echo "Project: $GOOGLE_CLOUD_PROJECT"
echo "Location: $GOOGLE_CLOUD_LOCATION"

APP_NAME=adk-streamlit-demo-test
STREAMLIT_ARTIFACT_REG_REPO=adk-streamlit-demo-test-repo
CONTAINER_PATH="us-central1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/${STREAMLIT_ARTIFACT_REG_REPO}/app"

echo "Building the application image..."
if ! gcloud artifacts repositories describe "$STREAMLIT_ARTIFACT_REG_REPO" \
       --location="$GOOGLE_CLOUD_LOCATION" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$STREAMLIT_ARTIFACT_REG_REPO" \
        --project="$GOOGLE_CLOUD_PROJECT" \
        --location="$GOOGLE_CLOUD_LOCATION" \
        --repository-format=docker
fi

# Submit the build to Cloud Build using the cloudbuild.yaml in the script's directory
gcloud builds submit --config cloudbuild.yaml --region "$GOOGLE_CLOUD_LOCATION" . --substitutions _CONTAINER_PATH="$CONTAINER_PATH"

echo 'Deploying the application to Cloud Run...'
gcloud run deploy "$APP_NAME" \
  --image "$CONTAINER_PATH:latest" \
  --min-instances 1 \
  --max-instances 1 \
  --cpu 1 \
  --memory 4Gi \
  --region us-central1 \
  --update-env-vars GCP_PROJECT="$GOOGLE_CLOUD_PROJECT",GCP_REGION="$GOOGLE_CLOUD_LOCATION",GOOGLE_CLOUD_AGENT_ENGINE_ID="projects/PROJECT_ID/locations/us-central1/reasoningEngines/RUNTIME_ID"

echo 'Deployment Done.'

echo "Follow these steps to open the app from Cloud Shell:
1. Open Cloud Shell from the Google Cloud Console.
2. Run: gcloud run services proxy $APP_NAME --project $GOOGLE_CLOUD_PROJECT --region $GOOGLE_CLOUD_LOCATION
3. In Cloud Shell, click the 'Web Preview' button on the toolbar.
4. Select 'Preview on port 8080'
5. A new browser tab or window will open, displaying your Streamlit app.
"
