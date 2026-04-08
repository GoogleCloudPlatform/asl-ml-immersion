#!/bin/bash
set -e

# USAGE: ./scripts/setup_kernel.sh <PROJECT_DIR> <ENV_NAME> <DISPLAY_NAME> [remove]

PROJECT_DIR_RAW=$1

PROJECT_DIR=$(cd "$PROJECT_DIR_RAW" && pwd)

ENVNAME=$2
DISPLAY_NAME=$3
ACTION=$4
PYTHON_VERSION=3.12

VENV_DIR=".venv"
VENV_PYTHON="${PROJECT_DIR}/${VENV_DIR}/bin/python"
VENV_BIN="${PROJECT_DIR}/${VENV_DIR}/bin"

# Move into the project directory for operations
cd "$PROJECT_DIR"

# --- REMOVE MODE ---
if [ "$ACTION" == "remove" ]; then
    echo "Removing kernel spec: $ENVNAME"
    jupyter kernelspec remove "$ENVNAME" -f || true
    echo "Removing venv in $PROJECT_DIR..."
    rm -rf "$VENV_DIR"
    exit 0
fi

# --- INSTALL MODE ---
echo "--- Setting up $ENVNAME in $PROJECT_DIR ---"

# 1. Create Venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    uv venv "$VENV_DIR" --python "$PYTHON_VERSION" --prompt "$ENVNAME"
fi

# 2. Install Dependencies
echo "Installing dependencies..."
uv pip install -p "$VENV_PYTHON" "Cython<3"

if [ -f "requirements.lock" ]; then
    echo "Installing dependencies from requirements.lock..."
    uv pip install -p "$VENV_PYTHON" pip -r requirements.lock -e .
else
    echo "Installing dependencies from requirements.txt..."
    uv pip install -p "$VENV_PYTHON" pip -r requirements.txt -e .
fi

if [ -f "requirements-without-deps.txt" ]; then
    uv pip install -p "$VENV_PYTHON" -U --no-deps -r requirements-without-deps.txt
fi

# 3. Register Kernel
echo "Registering Jupyter Kernel '$DISPLAY_NAME'..."

NEW_PATH="${VENV_BIN}:${PATH}"

"$VENV_PYTHON" -m ipykernel install \
    --user \
    --name="$ENVNAME" \
    --display-name="$DISPLAY_NAME" \
    --env PATH "$NEW_PATH"

echo "Kernel '$DISPLAY_NAME' is ready."
