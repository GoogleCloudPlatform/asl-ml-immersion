#!/bin/bash
#
# To build the kernel:  ./kernels/tf_privacy.sh
# To remove the kernel: ./kernels/tf_privacy.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

PROJECT_DIR=asl_core/notebooks/responsible_ai
ENVNAME=tf_privacy_kernel
KERNEL_DISPLAY_NAME="TF Privacy Kernel"
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
uv pip install -p "$VENV_PYTHON" tensorflow==2.14.0
uv pip install -p "$VENV_PYTHON" --no-deps tensorflow-privacy==0.8.12 dp_accounting==0.4.3 tensorflow_probability==0.22.0
uv pip install -p "$VENV_PYTHON" numpy==1.23.5 scipy~=1.9 dm-tree==0.1.8 attrs==25.3.0 cloudpickle==3.1.1 scikit-learn==1.*

NEW_PATH="${VENV_BIN}:${PATH}"

"$VENV_PYTHON" -m ipykernel install \
    --user \
    --name="$ENVNAME" \
    --display-name="$KERNEL_DISPLAY_NAME" \
    --env PATH "$NEW_PATH"

echo "Kernel '$KERNEL_DISPLAY_NAME' is ready."
