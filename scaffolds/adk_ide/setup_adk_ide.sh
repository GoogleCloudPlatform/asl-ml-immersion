#!/bin/bash

export PATH=$PATH:~/.local/bin
cd ..
cd ..
mkdir .vscode
cp scaffolds/adk_ide/launch.json .vscode/
cp scaffolds/adk_ide/settings.json .vscode/
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

echo "⚙️  Configuring IDE extensions..."

# Define the binary name (it varies slightly by image version, this function finds it)
CODE_BIN=$(which code-oss-cloud-workstations || which code || which code-oss)

if [ -z "$CODE_BIN" ]; then
    echo "❌ Error: Could not find code-oss binary."
else
    echo "✅ Found IDE binary at: $CODE_BIN"
    
    # Install Python Extension (includes Debugger)
    # The --force flag ensures it updates if already present
    "$CODE_BIN" --install-extension ms-python.python --force
    echo "✅ Configured IDE extensions."
fi

echo "✅ ADK IDE configured successfully."