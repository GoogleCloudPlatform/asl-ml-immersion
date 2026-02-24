#!/bin/bash
export SERVICE_NAME="adk-cloud-run-v1"
export APP_NAME="weather_agent_v1"
export AGENT_PATH="./agent_01_tool_func"
export BUCKET_URI="gs://$GOOGLE_CLOUD_STORAGE_BUCKET"
!gsutil ls $BUCKET_URI || gsutil mb -l $GOOGLE_CLOUD_LOCATION $BUCKET_URI
adk deploy agent_engine \
        --project=$GOOGLE_CLOUD_PROJECT \
        --region=$GOOGLE_CLOUD_LOCATION \
        --display_name="My First Agent" \
        $AGENT_PATH
