# Advanced Solutions Lab

## Overview
This repository contains Jupyter notebooks meant to be run on Vertex AI. This is maintained by Google Cloud’s [Advanced Solutions Lab (ASL)](https://cloud.google.com/asl) team. [Vertex AI](https://cloud.google.com/vertex-ai) is the next generation AI Platform on the Google Cloud Platform.
The material covered in this repo will take a software engineer with no exposure to machine learning to an advanced level.  

In particular, the notebooks in this repository cover
- A wide range of model architectures (DNN, CNN, RNN, transformers, SNGP, etc.) targeting many data modalities (tabular, image, text, time-series) implemented mainly in Tensorflow and Keras.
- Tools on Google Cloud’s Vertex AI for operationalizing Tensorflow, Scikit-learn and PyTorch models at scale.

If you are new to machine learning or Vertex AI start here:  [Introduction to TensorFlow](https://github.com/GoogleCloudPlatform/asl-ml-immersion/tree/master/notebooks/introduction_to_tensorflow)


## Repository Structure
All notebooks are in the notebooks folder. This folder is organized by different ML topics. Each folder contains a labs and a solutions folder. Use the labs notebooks to test your coding skills by filling in TODOs and refer to the notebooks in the solutions folder to verify your code. 

We have three main folders described below:

```
├── kernels - contains kernel scripts needed for certain notebooks in lab folder 
├── notebooks - contains labs and solutions notebook organized by topic 
│   ├── bigquery
│   ├── building_production_ml_systems
│   ├── docker_and_kubernetes
│   ├── . . .
├── scripts - contains setup scripts for enabling and setting up services on Vertex AI
```

For a more detailed breakdown of the notebooks in this repo, please refer to this [readme](https://github.com/GoogleCloudPlatform/asl-ml-immersion/blob/master/notebooks/README.md).


## Environment Setup (Vertex AI)
The code in this repository is designed to run on [Vertex AI Workbench User Managed Notebooks](https://cloud.google.com/vertex-ai/docs/workbench/user-managed/introduction), and tested on the “TensorFlow Enterprise 2.8” image. Please follow the instruction of [the official documentation](https://cloud.google.com/vertex-ai/docs/workbench/user-managed/create-user-managed-notebooks-instance-console-quickstart)  to set up a JupyterLab instance.

Accelerators (GPU/TPU) are not required in most of the labs, but some notebooks recommend using them.
After creating a Vertex Workbench User Managed Notebook instance, open the terminal and run the following commands.
```
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
export PATH=/home/jupyter/.local/bin:$PATH
make install
```
Note: Some notebooks might require additional setup, please refer to the instructions in specific notebooks.


## Contributions
Currently, only Googlers can contribute to this repo. See CONTRIBUTING.md for more details on the contribution workflow.


## Disclaimer
This is not an officially supported Google product. Usage of Google Cloud products will incur charges. Learn more about pricing [here](https://cloud.google.com/pricing). 

## Licensing
All the code in  this repo is licensed under the Apache License, Version 2.0 (the "License"). You may obtain a copy of the License [here](https://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License




