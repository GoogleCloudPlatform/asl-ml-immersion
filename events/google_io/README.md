# Advanced Solutions Lab

## Overview
This repository contains Jupyter notebooks meant to be run on Vertex AI. This is maintained by Google Cloud’s [Advanced Solutions Lab (ASL)](https://cloud.google.com/asl) team. [Vertex AI](https://cloud.google.com/vertex-ai) is the next generation AI Platform on the Google Cloud Platform.
The material covered in this repo will take a software engineer with no exposure to machine learning to an advanced level.

## Environment Setup (Vertex AI)

Follow the instruction of [the official documentation](https://cloud.google.com/vertex-ai/docs/workbench/user-managed/create-user-managed-notebooks-instance-console-quickstart) to set up a JupyterLab instance on [Vertex AI Workbench User Managed Notebooks](https://cloud.google.com/vertex-ai/docs/workbench/user-managed/introduction).
The code in this repository is designed to run on [Vertex AI Workbench User Managed Notebooks](https://cloud.google.com/vertex-ai/docs/workbench/user-managed/introduction), and tested on the `TensorFlow Enterprise 2.8` image.

After creating a Vertex Workbench User Managed Notebook instance, open the terminal *in your JupyterLab instance* and run the following commands:

```bash
git clone https://github.com/GoogleCloudPlatform/asl-ml-immersion.git
cd asl-ml-immersion
export PATH=$PATH:~/.local/bin
make install
```
