#!/bin/bash

SESSION_ID=$(curl -X POST http://localhost:8502/apps/agent_01_tool_func/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}' \
  | jq -r '.id')

echo "Session ID: $SESSION_ID"

curl -X POST http://localhost:8502/run \
-H "Content-Type: application/json" \
-d '{
"appName": "agent_01_tool_func",
"userId": "u_123",
"sessionId": "$SESSION_ID",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
