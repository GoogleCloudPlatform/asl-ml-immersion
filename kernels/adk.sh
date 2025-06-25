#!/bin/bash
#
# To build the kernel:  ./kernels/adk.sh
# To remove the kernel: ./kernels/adk.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

ENVNAME=adk_kernel
KERNEL_DISPLAY_NAME="ADK kernel"

source ~/.bashrc

# Cleaning up the kernel and exiting if first arg is 'remove'
if [ "$1" == "remove" ]; then
  echo Removing kernel $ENVNAME
  jupyter kernelspec remove $ENVNAME
  conda env remove -n $ENVNAME -y
  exit 0
fi

conda create -q -n $ENVNAME python=3.10.14 -y
conda activate $ENVNAME

# Install packages using a pip local to the conda environment.
conda install -q pip
pip install -q ipykernel

# Adds the conda kernel.
DL_ANACONDA_ENV_HOME="${DL_ANACONDA_HOME}/envs/$ENVNAME"
python -m ipykernel install --prefix "${DL_ANACONDA_ENV_HOME}" --name $ENVNAME --display-name "$KERNEL_DISPLAY_NAME"
rm -rf "${DL_ANACONDA_ENV_HOME}/share/jupyter/kernels/python3"

# Install packages
pip install google-adk==1.5.0 litellm==1.72.6

conda deactivate
