#!/bin/bash
#
# To build the kernel:  ./kernels/object_detection.sh
# To remove the kernel: ./kernels/object_detection.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

MODULE=vertex_genai
ENVNAME=langchain_kernel
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

pip install -q -U pip
pip install -q -U langchain==0.1.2
pip install -q -U langchain-google-vertexai==1.0.1
pip install -q -U chromadb
pip install -q -U pydantic==2.8.2
pip install -q -U google-cloud-aiplatform==1.48.0
pip install -q -U faiss-cpu==1.7.4
pip install -q -U unstructured==0.14.4
pip install -q -U wikipedia==1.4.0

deactivate
