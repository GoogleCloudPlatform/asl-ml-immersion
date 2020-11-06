# Continuous training with scikit-learn and Cloud AI Platform

This series of hands on labs guides you through the process of implementing a **Kubeflow Pipelines (KFP**) continuous training pipeline that automates training and deployment of a **scikit-learn** model. 

The below diagram represents the workflow orchestrated by the pipeline.

![Training pipeline](/images/kfp-caip.png).

1. The source data is in BigQuery
2. BigQuery is used to prepare training, evaluation, and testing data splits
3. AI Platform Training is used to tune hyperparameters and train a scikit-learn model
4. The model's performance is validated against a performance threshold
4. If the model meets or exceeds the performance threshold it is deployed as an online service using AI Platform Prediction

The ML model trained by the pipeline  is a multi-class classifier that predicts the type of  forest cover from cartographic data. The model is trained on the [Covertype Data Set](/datasets/covertype/README.md) dataset.

Before proceeding with the lab exercises you need to set up the lab environment and prepare the lab dataset.

## Preparing the lab environment
You will use the lab environment configured as on the below diagram:

![Lab env](/images/lab-env.png)

The core services in the environment are:
- ML experimentation and development - AI Platform Notebooks 
- Scalable, serverless model training - AI Platform Training  
- Scalable, serverless model serving - AI Platform Prediction 
- ML pipelines and ML metadata - AI Platform Pipelines
- Distributed data processing - Cloud Dataflow  
- Analytics data warehouse - BigQuery 
- Artifact store - Google Cloud Storage 
- CI/CD tooling - Cloud Build
    
In this environment, all services are provisioned in the same [Google Cloud Project](https://cloud.google.com/storage/docs/projects). 

### Enabling Cloud Services

To enable Cloud Services utilized in the lab environment:
1. Launch [Cloud Shell](https://cloud.google.com/shell/docs/launching-cloud-shell)
2. Set your project ID
```
PROJECT_ID=[YOUR PROJECT ID]

gcloud config set project $PROJECT_ID
```
3. Use `gcloud` to enable the services
```
gcloud services enable \
cloudbuild.googleapis.com \
container.googleapis.com \
cloudresourcemanager.googleapis.com \
iam.googleapis.com \
containerregistry.googleapis.com \
containeranalysis.googleapis.com \
ml.googleapis.com \
dataflow.googleapis.com 
```

The **Cloud Build** service account needs the Editor permissions in your GCP project to upload the pipeline package to an **AI Platform Pipelines** instance.

```
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUD_BUILD_SERVICE_ACCOUNT="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member serviceAccount:$CLOUD_BUILD_SERVICE_ACCOUNT \
  --role roles/editor
```

### Creating an instance of AI Platform Pipelines
The core component of the lab environment is **AI Platform Pipelines**. To create an instance of **AI Platform Pipelines** follow the [Setting up AI Platform Pipelines](https://cloud.google.com/ai-platform/pipelines/docs/setting-up) how-to guide. Make sure to enable the access to *https://www.googleapis.com/auth/cloud-platform* when creating a GKE cluster.


### Creating an instance of AI Platform Notebooks

An instance of **AI Platform Notebooks** is used as a primary experimentation/development workbench. The instance is configured using a custom container image that includes all Python packages required for the hands-on labs. 


1. In [Cloud Shell](https://cloud.google.com/shell/docs/launching-cloud-shell), create a folder in your `home` directory
```
cd
mkdir tmp-workspace
cd tmp-workspace
```
2. Create a requirements file with the Python packages to install in the custom image
```
cat > requirements.txt << EOF
kfp==0.2.5
fire
gcsfs
EOF
```
3. Create a Dockerfile defining you custom container image
```
cat > Dockerfile << EOF
FROM gcr.io/deeplearning-platform-release/base-cpu
SHELL ["/bin/bash", "-c"]
RUN apt-get update -y && apt-get -y install kubectl
COPY requirements.txt .
RUN python -m pip install -U -r requirements.txt 
EOF
```
4. Build the image and push it to your project's **Container Registry**
```
IMAGE_NAME=kfp-dev
TAG=latest
IMAGE_URI="gcr.io/${PROJECT_ID}/${IMAGE_NAME}:${TAG}"

gcloud builds submit --timeout 15m --tag ${IMAGE_URI} .
```
5. Create an instance of **AI Platform Notebooks**. Note that you can also create an instance using [GCP Console](https://cloud.google.com/ai-platform/notebooks/docs/custom-container)
```
ZONE=[YOUR_ZONE]
INSTANCE_NAME=[YOUR_INSTANCE_NAME]

IMAGE_FAMILY="common-container"
IMAGE_PROJECT="deeplearning-platform-release"
INSTANCE_TYPE="n1-standard-4"
METADATA="proxy-mode=service_account,container=$IMAGE_URI"

gcloud compute instances create $INSTANCE_NAME \
    --zone=$ZONE \
    --image-family=$IMAGE_FAMILY \
    --machine-type=$INSTANCE_TYPE \
    --image-project=$IMAGE_PROJECT \
    --maintenance-policy=TERMINATE \
    --boot-disk-device-name=${INSTANCE_NAME}-disk \
    --boot-disk-size=100GB \
    --boot-disk-type=pd-ssd \
    --scopes=cloud-platform,userinfo-email \
    --metadata=$METADATA
```

6. After the instance is created, you can connect to [JupyterLab](https://jupyter.org/) IDE by clicking the *OPEN JUPYTERLAB* link in the [AI Platform Notebooks Console](https://console.cloud.google.com/ai-platform/notebooks/instances).

7. In the **JupyterLab**, open a terminal and clone this repository in the `home` folder.
```
cd home
git clone https://github.com/GoogleCloudPlatform/mlops-on-gcp.git
```


## Preparing the lab dataset
The pipeline ingests data from BigQuery. Before proceeding with the labs upload the *Covertype* dataset to BigQuery:

1. In the **JupyterLab**, open a **JupyterLab** terminal.

2. Create the BigQuery dataset and upload the *Covertype* csv file.
```
export PROJECT_ID=$(gcloud config get-value core/project)

DATASET_LOCATION=US
DATASET_ID=covertype_dataset
TABLE_ID=covertype
DATA_SOURCE=gs://workshop-datasets/covertype/small/dataset.csv
SCHEMA=Elevation:INTEGER,\
Aspect:INTEGER,\
Slope:INTEGER,\
Horizontal_Distance_To_Hydrology:INTEGER,\
Vertical_Distance_To_Hydrology:INTEGER,\
Horizontal_Distance_To_Roadways:INTEGER,\
Hillshade_9am:INTEGER,\
Hillshade_Noon:INTEGER,\
Hillshade_3pm:INTEGER,\
Horizontal_Distance_To_Fire_Points:INTEGER,\
Wilderness_Area:STRING,\
Soil_Type:STRING,\
Cover_Type:INTEGER

bq --location=$DATASET_LOCATION --project_id=$PROJECT_ID mk --dataset $DATASET_ID

bq --project_id=$PROJECT_ID --dataset_id=$DATASET_ID load \
--source_format=CSV \
--skip_leading_rows=1 \
--replace \
$TABLE_ID \
$DATA_SOURCE \
$SCHEMA
```


## Summary of lab exercises

### Lab-01 - Using custom containers with AI Platform Training
In this lab, you will develop, package as a docker image, and run on AI Platform Training a training application that builds a **scikit-learn** classifier. The goal of this lab is to understand and codify the steps of the machine learning workflow that will be orchestrated by the continuous training pipeline.


### Lab-02 - Implementing continuous training pipeline with Kubeflow Pipelines and Cloud AI Platform
In this lab, you will author, deploy, and run a **Kubeflow Pipelines (KFP)** pipeline that automates ML workflow steps you experminted with in the first lab.

### Lab-03 - CI/CD for the continuous training pipeline
In this lab, you will author a **Cloud Build** CI/CD workflow that automates the process of building and deploying of the KFP pipeline authored in the second lab. You will also integrate the **Cloud Build** workflow with **GitHub**.



