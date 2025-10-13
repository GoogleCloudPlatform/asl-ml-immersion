#!/bin/bash
#
# To build the kernel:  ./kernels/adk_mcp_a2a.sh
# To remove the kernel: ./kernels/adk_mcp_a2a.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

ENVNAME=adk_mcp_a2a_kernel
KERNEL_DISPLAY_NAME="ADK MCP A2A Kernel"

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
pip install -q a2a-sdk==0.2.16 google-cloud-aiplatform[agent_engines]==1.115.0 google-adk==1.15.1
pip install -q langchain-community==0.3.25 python-dotenv==1.1.0 stackapi==0.3.1 toolbox-core==0.1.0
pip install -q gradio==5.49.1

conda deactivate
