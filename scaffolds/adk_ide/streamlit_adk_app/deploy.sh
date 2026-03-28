#!/bin/bash
export PATH=$PATH:~/.local/bin
pwd
[ ! -f ../.env ] || export $(grep -v '^#' ../.env | xargs)
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_LOCATION

APP_NAME=adk-streamlit-demo-test
STREAMLIT_ARTIFACT_REG_REPO=adk-streamlit-demo-test-repo

CONTAINER_PATH=us-central1-docker.pkg.dev/$GOOGLE_CLOUD_PROJECT/$STREAMLIT_ARTIFACT_REG_REPO/app

echo "Building the application image..."
if ! gcloud artifacts repositories describe $STREAMLIT_ARTIFACT_REG_REPO \
       --location=$GOOGLE_CLOUD_LOCATION; then
    gcloud artifacts repositories create $STREAMLIT_ARTIFACT_REG_REPO \
        --project=$GOOGLE_CLOUD_PROJECT --location=$GOOGLE_CLOUD_LOCATION --repository-format=docker
fi

echo $_CONTAINER_PATH
gcloud builds submit --config cloudbuild.yaml --region $GOOGLE_CLOUD_LOCATION . --substitutions _CONTAINER_PATH=$CONTAINER_PATH

echo 'Deploying the application to Cloud Run...'
gcloud run deploy $APP_NAME \
  --image $CONTAINER_PATH:latest --min-instances 1 --max-instances 1 --cpu 1 \
  --memory 4Gi --region us-central1 \
  --no-allow-unauthenticated \
  --invoker-iam-check \
  --update-env-vars GCP_PROJECT=$GOOGLE_CLOUD_PROJECT,GCP_REGION=$GOOGLE_CLOUD_LOCATION

echo 'Deployment Done.'

echo "Follow these steps to open the app from Cloud Shell.
1. Open Cloud Shell from the Google Cloud Console.
2. Run 'gcloud run services proxy $APP_NAME --project $GOOGLE_CLOUD_PROJECT --region $GOOGLE_CLOUD_LOCATION'.
2. In Cloud Shell, click the 'Web Preview' button on the toolbar.
3. Select 'Preview on port 8080'
4. A new browser tab or window will open, displaying your Streamlit app.
"
