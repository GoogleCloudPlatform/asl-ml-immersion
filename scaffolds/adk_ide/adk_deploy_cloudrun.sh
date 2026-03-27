#!/bin/bash
export PATH=$PATH:~/.local/bin
export SERVICE_NAME="adk-cloud-run-api-server"
export APP_NAME="agent_01_tool_func"
export AGENT_PATH="./agent_01_tool_func"
pwd
[ ! -f .env ] || export $(grep -v '^#' .env | xargs)
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_LOCATION
adk deploy cloud_run \
--project=$GOOGLE_CLOUD_PROJECT \
--region=$GOOGLE_CLOUD_LOCATION \
--service_name=$SERVICE_NAME \
--app_name=$APP_NAME \
$AGENT_PATH
