#!/bin/bash
#
# To build the kernel:  ./kernels/reinforcement_learning.sh
# To remove the kernel: ./kernels/reinforcement_learning.sh remove
#
# This scripts will create a ipython kernel named $MODULE
# populated with the reqs in ./notebooks/$MODULE/requirements.txt


MODULE=recommendation_systems
ENVNAME=tf_recommenders_kernel
REPO_ROOT_DIR="$(dirname $(cd $(dirname $BASH_SOURCE) && pwd))"

# Cleaning up the kernel and exiting if first arg is 'remove'
if [ "$1" == "remove" ]; then
  echo Removing kernel $ENVNAME
  jupyter kernelspec remove $MODULE_NAME
  rm -r "$REPO_ROOT_DIR/notebooks/$MODULE/$ENVNAME"
  exit 0
fi

cd $REPO_ROOT_DIR/notebooks/$MODULE

# Setup virtual env and kernel
echo creating $ENVNAME at $(pwd)
python3 -m venv $ENVNAME

# Registering the venv as an ipython kernel
source $ENVNAME/bin/activate
pip install -U pip
pip install ipykernel
python -m ipykernel install --user --name=$ENVNAME

# Install TF Recommenders, TF-Datasets, and scann and its dependencies
pip install tensorflow-recommenders==0.7.2
pip install -U tensorflow-datasets==4.7.0
pip install scann==1.2.9

deactivate
