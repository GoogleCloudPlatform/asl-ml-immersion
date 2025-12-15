# Quick Start (Local Testing)

Install required packages and launch the local development environment:

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
export PATH=$PATH:~/.local/bin
mkdir .vscode
cp scaffolds/adk_ide/launch.json .vscode/
cd mcp-toolbox
export VERSION=0.13.0
curl -O https://storage.googleapis.com/genai-toolbox/v$VERSION/linux/amd64/toolbox
chmod +x toolbox
cd ..
cd scaffolds/adk_ide
make install
export PATH=$PATH:~/.local/bin
make install
source .venv/bin/activate
export PROJECT_ID=$(curl -s "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
echo $PROJECT_ID
gcloud config set project $PROJECT_ID
export GOOGLE_CLOUD_PROJECT=$PROJECT_ID
export CLOUDSDK_CORE_PROJECT=$GOOGLE_CLOUD_PROJECT
echo $CLOUDSDK_CORE_PROJECT
gcloud config set project $CLOUDSDK_CORE_PROJECT
cp env.example .env
sed -i "s/^# GOOGLE_CLOUD_PROJECT=.*/GOOGLE_CLOUD_PROJECT=$PROJECT_ID/" .env
#vim .env # Uncomment and update the environment variables
```

If you are using Vertex AI, make sure you are authenticated with `gcloud`:

```bash
gcloud config set project <your-dev-project-id>
```

# Testing API Server with curl

## Create a session

```bash
SESSION_ID=$(curl -X POST http://localhost:8502/apps/agent_01_tool_func/users/u_123/sessions/s_123 \
  -H "Content-Type: application/json" \
  -d '{"key1": "value1", "key2": 42}' \
  | jq -r '.id')
```
## Print the session ID

```bash
echo "Session ID: $SESSION_ID"
```

# Execute a query with curl

```bash
curl -X POST http://localhost:8502/run \
-H "Content-Type: application/json" \
-d '{
"appName": "agent_01_tool_func",
"userId": "u_123",
"sessionId": "s_123",
"newMessage": {
    "role": "user",
    "parts": [{
    "text": "Hey whats the weather in new york today"
    }]
}
}'
```

## Commands

| Command              | Description                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Install all required dependencies using uv                                                  |
| `make playground`    | Launch local development environment with backend and frontend - leveraging `adk web` command.|
| `make backend`       | Deploy agent to Cloud Run |

For full command options and usage, refer to the [Makefile](Makefile).
