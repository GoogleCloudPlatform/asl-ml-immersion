#!/bin/bash
export SERVICE_NAME="adk-cloud-run-v1"
export APP_NAME="weather_agent_v1"

export ADK_CUSTOM_IMAGE_APP_NAME="adk-custom-image-demo-agent"
#  --add-cloudsql-instances $GOOGLE_CLOUD_PROJECT:us-central1:adk-demo-session-service \
#   --update-env-vars SERVE_WEB_INTERFACE=True,SESSION_SERVICE_URI=$SESSION_SERVICE_URI,GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT


gcloud run deploy capital-agent-service \
--source . \
--port 8080 \
--memory 4G \
--region $GOOGLE_CLOUD_LOCATION \
--project $GOOGLE_CLOUD_PROJECT \
--no-allow-unauthenticated \
--set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI"
# Add any other necessary environment variables your agent might need