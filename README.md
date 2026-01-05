# Advanced Solutions Lab

## Overview
This repository contains AI and Machine Learning contents meant to be run on Google Cloud. This is maintained by Google Cloud’s [Advanced Solutions Lab (ASL)](https://cloud.google.com/asl) team. 

In particular, the notebooks in this repository cover
- `asl_core`: A wide range of model architectures (DNN, CNN, RNN, transformers, SNGP, etc.) targeting many data modalities (tabular, image, text, time-series) implemented mainly in Tensorflow and Keras.
- `asl_mlops`: Tools on Google Cloud’s Vertex AI for operationalizing Tensorflow, Scikit-learn and PyTorch models at scale (e.g. Vertex training, tuning, and serving, TFX and Kubeflow pipelines).
- `asl_agent`: Generative AI and Agent System using Gemini and Agentic Frameworks like Google ADK.

## Repository Structure
Each module (`asl_core`, `asl_mlops`, `asl_agent`) has separate environment and contents, which are organized in each directory. 

All learning materials are in the contets folder. This folder is organized by different topics. Each folder contains a `labs` and a `solutions` folder. Use the `labs` notebooks to test your coding skills by filling in TODOs and refer to the notebooks in the `solutions` folder to verify your code.

We have three main folders described below:

```
├── asl_core
|   ├── contents - contains learning materials organized by topic
│       ├── building_production_ml_systems
│           ├── labs
│           ├── solutions
│       ├── end-to-end-structured
│       ├── image_models
│       ├── ...
|   ├── kernels - contains kernel scripts needed for certain notebooks
|   ├── scaffolds - contains sample code to accelerate AI/ML projects
|   ├── requirements.txt - dependencies for this module
├── asl_mlops
|   ├── ...
├── asl_agent
|   ├── ...
├── ...
```

## Environment Setup
### Step 1. Create a Vertex Workbench or Cloud Workstations Environment
This repository is tested on Vertex AI Workbench and Cloud Workstations. Spin up either following these instructions.
#### Option A: Vertex AI Workbench
[Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/workbench/instances/introduction) is a managed Jupyter Lab environment. Follow [the official documentation](https://cloud.google.com/vertex-ai/docs/workbench/instances/create-console-quickstart) to set up a JupyterLab instance.

#### Option B: Cloud Workstations
[Cloud Workstations](https://cloud.google.com/workstations) is a fully managed development environments built to meet the needs of security-sensitive enterprises, while accelerating developer onboarding and productivity, including a native integration with Gemini for Google Cloud.

1. Follow [the official documentation](https://docs.cloud.google.com/workstations/docs/create-workstation) to set up a Cloud Workstations IDE. 
2. Launch a workstation, and install `Python` and `Jupyter` extensions from the `Extension` tab on the left.

**Note:** Accelerators (GPU/TPU) are not required in most of the labs, but some notebooks recommend using them.

### Step 2. User Authentication
After creating a Vertex Workbench Instance or Workbench, open the terminal and run the following commands to authenticate the user in the environemnt.

```bash
gcloud auth login --update-adc
gcloud config set project $(curl "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
```
The first command generate an authentication Link. Navigate to the link, login with your user, copy and paste the generated token back in the terminal.


### Step 3. Build the Environemnt
Then, run the commands below to clone this repository, and build the environemnt (venvs and jupyter kernels) for each module.

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
make
```

On Cloud Workstations, click `Open Folder` -> `asl-ml-immersion` to open the repository window. If the folder is already opend, click `Command + Shift + P` and type `Developer: Reload Window` to reflect the changes to the window.

## Using the Environment
### Running a notebook with built a kernel
After the setup above, you can open a Jupyter notebook file, and execute on a module kernel (`ASL Core`, `ASL MLOps`, or `ASL Agent`).

If a correct kernel is not pre-selected, click `Select Kernel` and select one. (On workbench, you can find a kernel under `Select Kernel` -> `Jupyter Kernels`) <br>
If you can't find `Jupyter Kernels` on Cloud Workstations, click `Python Environment` -> `<- (Left Arrow)` to reload the environment.

**Note**: Some notebooks might require additional setup, please refer to the instructions in specific notebooks.

### Running a command on Terminal
When running a command from the terminal, make sure to activate a venv for a specific environment.

E.g. (under asl-ml-immersion directory),
```bash
source ./asl_agent/.venv/bin/activate
adk web ./asl_agent/contents/vertex_genai/solutions/adk_agents
```

## Contributions
Currently, only Googlers can contribute to this repo. See [CONTRIBUTING.md](https://github.com/GoogleCloudPlatform/asl-ml-immersion/blob/master/CONTRIBUTING.md) for more details on the contribution workflow.


## Disclaimer
This is not an officially supported Google product. Usage of Google Cloud products will incur charges. Learn more about pricing [here](https://cloud.google.com/pricing).

## Licensing
All the code in  this repo is licensed under the Apache License, Version 2.0 (the "License"). You may obtain a copy of the License [here](https://www.apache.org/licenses/LICENSE-2.0).

*Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License*
