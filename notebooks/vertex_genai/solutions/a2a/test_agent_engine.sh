#!/bin/bash

# Source the .env file to get environment variables
if [ -f ".env" ]; then
  source .env
else
  echo "Error: .env file not found!"
  exit 1
fi

curl \
-H "Authorization: Bearer $(gcloud auth print-access-token)" \
-H "Content-Type: application/json" \
https://us-central1-aiplatform.googleapis.com/v1/${AGENT_ENGINE_RESOURCE_NAME}:streamQuery?alt=sse -d '{
  "class_method": "stream_query",
  "input": {
    "user_id": "user_123",
    "message": "List available burger menu please",
  }
}'
