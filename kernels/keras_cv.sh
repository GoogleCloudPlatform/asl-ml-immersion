#!/bin/bash
#
# To build the kernel:  ./kernels/keras_cv.sh
# To remove the kernel: ./kernels/keras_cv.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

MODULE=image_models
ENVNAME=keras_cv_kernel
REPO_ROOT_DIR="$(dirname $(cd $(dirname $BASH_SOURCE) && pwd))"

# Cleaning up the kernel and exiting if first arg is 'remove'
if [ "$1" == "remove" ]; then
  echo Removing kernel $ENVNAME
  jupyter kernelspec remove $ENVNAME
  rm -r "$REPO_ROOT_DIR/notebooks/$MODULE/$ENVNAME"
  exit 0
fi

cd $REPO_ROOT_DIR/notebooks/$MODULE

# Setup virtual env and kernel
python3 -m venv $ENVNAME --system-site-packages
source $ENVNAME/bin/activate
python -m ipykernel install --user --name=$ENVNAME

# Install Object Detection API and its dependencies
pip install -q keras-cv==0.9.0

deactivate
