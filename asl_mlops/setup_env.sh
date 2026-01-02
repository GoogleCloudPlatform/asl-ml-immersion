#!/bin/bash
#
# To build the kernel:  ./setup_env.sh
# To remove the kernel: ./setup_env.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

ENVNAME="asl_mlops"
DISPLAY_NAME="ASL MLOps Kernel"
VENV_DIR=".venv"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "$SCRIPT_DIR"

# Cleaning up the kernel and exiting if first arg is 'remove'
if [ "$1" == "remove" ]; then
    echo "Removing kernel spec: $ENVNAME"
    jupyter kernelspec remove "$ENVNAME" -f || true
    echo "Removing venv: $VENV_DIR"
    rm -rf "$VENV_DIR"
    exit 0
fi

# Setup virtual env and kernel
echo creating $ENVNAME at $(pwd)
uv venv "$VENV_DIR"

source $ENVNAME/bin/activate

echo "Installing dependencies with uv..."
uv pip install ipykernel -r requirements.txt -e .

echo "Registering Jupyter Kernel..."
python -m ipykernel install --user --name=$ENVNAME --display-name="$DISPLAY_NAME" --env PATH "$PATH"

deactivate
