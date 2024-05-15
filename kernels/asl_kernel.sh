#!/bin/bash
#
# To build the kernel:  ./kernels/asl_kernel.sh
# To remove the kernel: ./kernels/asl_kernel.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

ENVNAME=asl_kernel
DISPLAY_NAME="ASL Kernel"
REPO_ROOT_DIR="$(dirname $(cd $(dirname $BASH_SOURCE) && pwd))"

# Cleaning up the kernel and exiting if first arg is 'remove'
if [ "$1" == "remove" ]; then
  echo Removing kernel $ENVNAME
  jupyter kernelspec remove $ENVNAME
  rm -r "$REPO_ROOT_DIR/$ENVNAME"
  exit 0
fi

cd $REPO_ROOT_DIR

# Setup virtual env and kernel
echo creating $ENVNAME at $(pwd)
python3 -m venv $ENVNAME --system-site-packages

# Registering the venv as an ipython kernel
source $ENVNAME/bin/activate
pip install -U pip
pip install ipykernel
python -m ipykernel install --user --name=$ENVNAME --display-name="$DISPLAY_NAME"

# Install dependencies
pip install -U "Cython<3"
pip install -U -e .
pip install -U --no-deps -r requirements-without-deps.txt

sudo apt-get -y install graphviz

deactivate
