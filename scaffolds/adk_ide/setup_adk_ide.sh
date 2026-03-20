#!/bin/bash

export PATH=$PATH:~/.local/bin
cd ..
cd ..
mkdir .vscode
cp scaffolds/adk_ide/launch.json .vscode/
cp scaffolds/adk_ide/settings.json .vscode/
mkdir .devcontainer
cp scaffolds/adk_ide/devcontainer_template/Dockerfile .devcontainer/
cp scaffolds/adk_ide/devcontainer_template/devcontainer.json .devcontainer/
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

# Define the binary name (it varies across local VS Code, Cloud Workstations, or open-source builds)
CODE_BIN=$(which code-oss-cloud-workstations || which code || which code-oss)

if [ -z "$CODE_BIN" ]; then
    echo "❌ Error: Could not find IDE binary."
else
    echo "✅ Found IDE binary at: $CODE_BIN"
    
    # Install Python Extension
    echo "📦 Installing Python..."
    "$CODE_BIN" --install-extension ms-python.python --force

    # Install Dev Containers Extension (crucial for local/remote container dev)
    echo "📦 Installing Dev Containers..."
    "$CODE_BIN" --install-extension ms-vscode-remote.remote-containers --force

    # Install Ruff Extension (linter/formatter to pair with uv)
    echo "📦 Installing Ruff..."
    "$CODE_BIN" --install-extension charliermarsh.ruff --force
    
    echo "✅ Successfully configured IDE extensions."
fi

echo "✅ ADK IDE configured successfully."