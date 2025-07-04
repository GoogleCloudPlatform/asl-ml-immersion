#!/bin/bash
#
# To build the kernel:  ./kernels/tf_privacy.sh
# To remove the kernel: ./kernels/tf_privacy.sh remove
#
# This scripts will create a ipython kernel named $ENVNAME

ENVNAME=tf_privacy_kernel
KERNEL_DISPLAY_NAME="TF Privacy Kernel"

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
<<<<<<< HEAD:kernels/tf_privacy.sh
pip install tensorflow==2.14.0
pip install --no-deps tensorflow-privacy==0.8.12 dp_accounting==0.4.3 tensorflow_probability==0.22.0
pip install numpy==1.23.5 scipy~=1.9 dm-tree==0.1.8 attrs==25.3.0 cloudpickle==3.1.1 scikit-learn==1.*
=======
pip install google-adk==1.5.0 litellm==1.72.6
pip install google-cloud-aiplatform[evaluation]==1.101.0
pip install plotly==6.2.0 nbformat==5.10.4
>>>>>>> 59e93d3b (added vertex eval package to kernel):kernels/adk.sh

conda deactivate
