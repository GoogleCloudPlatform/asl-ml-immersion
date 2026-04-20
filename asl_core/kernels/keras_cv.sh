#!/bin/bash
#
# To build the kernel:  ./kernels/keras_cv.sh
# To remove the kernel: ./kernels/keras_cv.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

PROJECT_DIR=asl_core/notebooks/image_models
ENVNAME=keras_cv_kernel
KERNEL_DISPLAY_NAME="Keras CV Kernel"
PYTHON_VERSION=3.10.14

VENV_PYTHON="${ENVNAME}/bin/python"
VENV_BIN="${ENVNAME}/bin"

cd "$PROJECT_DIR"

# Cleaning up the kernel and exiting if first arg is 'remove'
if [ "$1" == "remove" ]; then
    echo "Removing kernel spec: $ENVNAME"
    jupyter kernelspec remove "$ENVNAME" -f || true
    echo "Removing venv $ENVNAME..."
    rm -rf "$ENVNAME"
    exit 0
fi

# Setup virtual env and kernel
uv venv "$ENVNAME" --python "$PYTHON_VERSION" --prompt "$KERNEL_DISPLAY_NAME"
uv pip install -p "$VENV_PYTHON" ipykernel 'setuptools<82' ipywidgets pexpect
uv pip install -p "$VENV_PYTHON" google-cloud-aiplatform 'numpy<2' matplotlib tensorflow[and-cuda]==2.14.0 keras-cv==0.9.0

NEW_PATH="${VENV_BIN}:${PATH}"

"$VENV_PYTHON" -m ipykernel install \
    --user \
    --name="$ENVNAME" \
    --display-name="$KERNEL_DISPLAY_NAME" \
    --env PATH "$NEW_PATH"

echo "Kernel '$KERNEL_DISPLAY_NAME' is ready."
