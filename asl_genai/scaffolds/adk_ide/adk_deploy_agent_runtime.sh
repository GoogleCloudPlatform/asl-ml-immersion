#!/bin/bash
source scaffolds/adk_ide/.venv/bin/activate
export PATH=$PATH:~/.local/bin
export SERVICE_NAME="adk-service-test"
export APP_NAME="agent_01_tool_func"
#export AGENT_PATH="./agent_01_tool_func"
export AGENT_PATH="./scaffolds/adk_ide/agent_01_tool_func"
pwd
[ ! -f ./scaffolds/adk_ide/.env ] || export $(grep -v '^#' ./scaffolds/adk_ide/.env | xargs)
echo $GOOGLE_CLOUD_PROJECT
echo $GOOGLE_CLOUD_LOCATION

adk deploy agent_engine --project=$GOOGLE_CLOUD_PROJECT --region=$GOOGLE_CLOUD_LOCATION --display_name="My First Agent" $AGENT_PATH