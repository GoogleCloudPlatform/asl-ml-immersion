#!/bin/bash

# Usage: ./create_new_project.sh <project_name>

if [ -z "$1" ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

PROJECT_NAME=$1
PARENT_DIR=$(dirname "$(realpath "$0")")
PROJECT_DIR="${PARENT_DIR}/${PROJECT_NAME}"

if [ -d "$PROJECT_DIR" ]; then
    echo "Error: Directory ${PROJECT_DIR} already exists."
    exit 1
fi

mkdir -p "${PROJECT_DIR}"

# Create __init__.py
cat << 'EOF' > "${PROJECT_DIR}/__init__.py"
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
EOF

# Create tools.py
cat << 'EOF' > "${PROJECT_DIR}/tools.py"
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Tools for the agent.
"""

EOF

# Create agent.py
cat << 'EOF' > "${PROJECT_DIR}/agent.py"
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent

MODEL = "gemini-2.5-flash"

# Import your tools here:
# from .tools import my_tool

root_agent = Agent(
    name="empty_agent",
    model=MODEL,
    description="An empty agent template.",
    instruction="You are a helpful assistant.",
    tools=[],
)
EOF

echo "Successfully created adk project: ${PROJECT_NAME}"
