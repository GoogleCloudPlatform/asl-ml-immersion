#!/bin/bash
export SERVICE_NAME="adk-cloud-run-v1"
export APP_NAME="weather_agent_v1"
export AGENT_PATH="./agent_01_tool_func"
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=$SERVICE_NAME \
--app_name=$APP_NAME \
--with_ui \
$AGENT_PATH
