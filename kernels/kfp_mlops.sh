#!/bin/bash
#
# To build the kernel:  ./kernels/kfp_mlops.sh
# To remove the kernel: ./kernels/kfp_mlops.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

ENVNAME=adk_kernel
KERNEL_DISPLAY_NAME="MLOps kernel"

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
pip install kfp==2.4.0
pip install google-cloud-pipeline-components==2.8.0
# Utilities
pip install pyyaml==5.3.1
pip install pydantic==2.9.2
pip install pypdf==4.3.1
pip install fire==0.6.0
# Google Cloud
pip google-genai==1.7.0
pip google-api-core==2.24.0
pip google-cloud-storage==2.19.0
pip google-cloud-aiplatform==1.85.0
pip google-cloud-bigquery==3.21.0
pip cloudml-hypertune
pip apache-beam==2.46.0

conda deactivate
