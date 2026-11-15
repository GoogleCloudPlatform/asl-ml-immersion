#!/bin/bash
export PATH=$PATH:~/.local/bin
cd mcp-toolbox
export VERSION=1.1.0
curl -L -o toolbox https://storage.googleapis.com/mcp-toolbox-for-databases/v$VERSION/linux/amd64/toolbox
chmod +x toolbox
echo "✅ mcp-toolbox downloaded successfully."
echo "Configure a tools.yaml to define your tools, and then execute toolbox to start the server:" 
echo "./mcp-toolbox/toolbox --config ./mcp-toolbox/tools.yaml"