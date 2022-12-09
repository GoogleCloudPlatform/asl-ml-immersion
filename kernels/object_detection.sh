#!/bin/bash
ENVNAME=object_detection_kernel

cd ~/asl-ml-immersion/notebooks/image_models/solutions

# Download the Object Detection API
git clone --depth 1 https://github.com/tensorflow/models
cd models/research/
protoc object_detection/protos/*.proto --python_out=.
cp object_detection/packages/tf2/setup.py .

# Setup virtual env and kernel
python3 -m venv $ENVNAME --system-site-packages
source $ENVNAME/bin/activate
python -m ipykernel install --user --name=$ENVNAME

# Install Object Detection API and its dependencies
pip install -U pip
pip install .

deactivate
