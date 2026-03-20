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

echo "⚙️  Detecting environment and configuring IDE extensions..."

# 1. Detect the environment by checking available binaries
if command -v code-oss-cloud-workstations &> /dev/null; then
    echo "☁️  Environment detected: Google Cloud Workstation"
    CODE_BIN="code-oss-cloud-workstations"
    IS_LOCAL=false
elif command -v code &> /dev/null; then
    echo "💻 Environment detected: Local VS Code"
    CODE_BIN="code"
    IS_LOCAL=true
elif command -v code-oss &> /dev/null; then
    echo "🐧 Environment detected: VS Code OSS / VDI"
    CODE_BIN="code-oss"
    IS_LOCAL=false
else
    echo "❌ Error: Could not find any IDE binary."
    exit 1
fi

echo "⚙️  Configuring IDE extensions..."

# Define the binary name (it varies across local VS Code, Cloud Workstations, or open-source builds)
CODE_BIN=$(which code-oss-cloud-workstations || which code || which code-oss)

if [ -z "$CODE_BIN" ]; then
    echo "❌ Error: Could not find IDE binary."
else
    echo "✅ Found IDE binary at: $CODE_BIN"

    # 2. Conditionally install the Dev Containers extension
    if [ "$IS_LOCAL" = true ]; then
        echo "📦 Installing Dev Containers extension..."
        mkdir -p .devcontainer
        cp scaffolds/adk_ide/devcontainer_template/Dockerfile .devcontainer/
        cp scaffolds/adk_ide/devcontainer_template/devcontainer.json .devcontainer/
        "$CODE_BIN" --install-extension ms-vscode-remote.remote-containers --force
    else
        echo "⏩ Skipping Dev Containers extension (Native to Cloud / Not on Open VSX)."
    fi  
    
    # Install Python Extension
    echo "📦 Installing Python..."
    "$CODE_BIN" --install-extension ms-python.python --force

    # Install Ruff Extension (linter/formatter to pair with uv)
    echo "📦 Installing Ruff..."
    "$CODE_BIN" --install-extension charliermarsh.ruff --force
    
    echo "✅ Successfully configured IDE extensions."
fi

echo "✅ ADK IDE configured successfully."