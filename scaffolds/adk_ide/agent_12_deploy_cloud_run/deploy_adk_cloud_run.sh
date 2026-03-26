#!/bin/bash
export SERVICE_NAME="adk-cloud-run-v1"
export APP_NAME="weather_agent_v1"
#export AGENT_PATH="./agent_01_tool_func"
export GOOGLE_CLOUD_PROJECT="PUT_YOUR_PROJECT_ID_HERE"
export GOOGLE_CLOUD_LOCATION="us-central1"
export ADK_CUSTOM_IMAGE_APP_NAME="adk-custom-image-demo-agent"
#  --add-cloudsql-instances $GOOGLE_CLOUD_PROJECT:us-central1:adk-demo-session-service \
#   --update-env-vars SERVE_WEB_INTERFACE=True,SESSION_SERVICE_URI=$SESSION_SERVICE_URI,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT
gcloud run deploy $ADK_CUSTOM_IMAGE_APP_NAME \
  --source . \
  --port 8080 \
  --memory 4G \
  --project=$GOOGLE_CLOUD_PROJECT \
  --region=$GOOGLE_CLOUD_LOCATION \
  --allow-unauthenticated \
  --update-env-vars SERVE_WEB_INTERFACE=True,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT