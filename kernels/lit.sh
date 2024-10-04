#!/bin/bash
#
# To build the kernel:  ./kernels/lit.sh
# To remove the kernel: ./kernels/lit.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

ENVNAME=lit_kernel
KERNEL_DISPLAY_NAME="LIT kernel"

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

pip install -q tensorflow==2.14.1 lit-nlp keras_nlp

conda deactivate
