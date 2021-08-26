# Continuous training with TFX and Cloud AI Platform

This series of hands on labs guides you through the process of implementing a TensorFlow Extended (TFX) continuous training pipeline that automates training and deployment of a TensorFlow 2.3 model.

The below diagram represents the workflow orchestrated by the pipeline.

![TFX_CAIP](/images/tfx-caip.png).

1. Training data in the CSV format is ingested from a GCS location using *CsvExampleGen*. The URI to the data root is passed as a runtime parameter. The *CsvExampleGen* component splits the source data into training and evaluation splits and converts the data into the TFRecords format.
2. The *StatisticsGen* component generates statistics for both splits.
3. The *SchemaGen* component autogenerates a schema . This is done for data validation and anomaly detection. The pipeline uses a curated schema imported by the *ImportedNode* component.
4. The *ImporterNode* component is used to bring the curated schema file into the pipeline. The location of the schema file is passed as a runtime parameter. 
5. The *ExampleValidator* component validates the generated examples against the imported schema
6. The *Transform* component preprocess the data to the format required by the *Trainer* component. It also saves the preprocessing TensorFlow graph for consistent feature engineering at training and serving time.
7. The *Trainer* starts an AI Platform Training job. The AI Platform Training job is configured for training in a custom container. 
8. The *Tuner* component in the example pipeline tunes model hyperparameters using CloudTuner (KerasTuner instance) and AI Platform Vizier as a back-end. It can added and removed from the pipeline using the `enable_tuning` environment variable set in the notebook or in the pipeline code. When included in the pipeline, it ouputs a "best_hyperparameter" artifact directly into the *Trainer*. When excluded hyperparameters are drawn from the defaults set in the pipeline code.
9. The *ResolverNode* component retrieves the best performing model from the previous runs and passed it to the *Evaluator* to be used as a baseline during model validation.
10. The *Evaluator* component evaluates the trained model against the eval split and validates against the baseline model from the *ResolverNode*. If the new model exceeds validation thresholds it is marked as "blessed".
11. The *InfraValidator* component validates the model serving infrastructure and provides a "infra_blessing" that the model can be loaded and queried for predictions.
12. If the new model is blessed by the *Evaluator* and *InfraValidator*, the *Pusher* deploys the model to AI Platform Prediction.

The ML model utilized in the labs  is a multi-class classifier that predicts the type of  forest cover from cartographic data. The model is trained on the [Covertype Data Set](/datasets/covertype/README.md) dataset.

## Preparing the lab environment
You will use the lab environment configured as on the below diagram:

![Lab env](/images/lab-env.png)

The core services in the environment are:
- ML experimentation and development - AI Platform Notebooks 
- Scalable, serverless model training - AI Platform Training  
- Parallelized and distributed model hyperparameter tuning - AI Platform Vizier   
- Scalable, serverless model serving - AI Platform Prediction 
- Machine learning pipelines - AI Platform Pipelines
- Distributed data processing - Cloud Dataflow
- Artifact store - Google Cloud Storage 
- CI/CD tooling - Cloud Build
    
In this environment, all services are provisioned in the same [Google Cloud Project](https://cloud.google.com/storage/docs/projects). 

### Enabling Cloud Services

To enable Cloud Services utilized in the lab environment:

1. Launch [Cloud Shell](https://cloud.google.com/shell/docs/launching-cloud-shell)
t
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

4. The **Cloud Build** service account needs the Editor permissions in your GCP project to upload the pipeline package to an **AI Platform Pipelines** instance.
```
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUD_BUILD_SERVICE_ACCOUNT="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member serviceAccount:$CLOUD_BUILD_SERVICE_ACCOUNT \
  --role roles/editor
```

5. Create a custom service account to give CAIP training job access to AI Platform Vizier service for pipeline hyperparameter tuning.
```
SERVICE_ACCOUNT_ID=tfx-tuner-caip-service-account
gcloud iam service-accounts create $SERVICE_ACCOUNT_ID  \
    --description="A custom service account for CAIP training job to access AI Platform Vizier service for pipeline hyperparameter tuning" \
    --display-name="TFX Tuner CAIP Vizier"
```

6. Grant your custom service account access to the `ml.admin` role to create and manage AI Platform Vizier studies.
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com \
    --role=roles/ml.admin
```

7. Grant your custom service account access to the `storage.objectAdmin` role for artifact access and temporary tuning file storage.
```
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member=serviceAccount:${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com \
    --role=roles/storage.objectAdmin
```

8. Grant your project's AI Platform Google-managed service account the `iam.serviceAccountAdmin` role for your new custom service account. To do so, use the gcloud tool to run the following command:
```
gcloud iam service-accounts add-iam-policy-binding \
  --role=roles/iam.serviceAccountAdmin \
  --member=serviceAccount:service-${PROJECT_NUMBER}@cloud-ml.google.com.iam.gserviceaccount.com \
  ${SERVICE_ACCOUNT_ID}@${PROJECT_ID}.iam.gserviceaccount.com
```


### Creating an instance of AI Platform Pipelines
The core component of the lab environment is **AI Platform Pipelines**. To create an instance of **AI Platform Pipelines** follow the [Setting up AI Platform Pipelines](https://cloud.google.com/ai-platform/pipelines/docs/setting-up) how-to guide. Make sure to enable the access to *https://www.googleapis.com/auth/cloud-platform* when creating a GKE cluster.


### Creating an instance of AI Platform Notebooks

An instance of **AI Platform Notebooks** is used as a primary experimentation/development workbench.

To provision the instance follow the [Create an new notebook instance](https://cloud.google.com/ai-platform/notebooks/docs/create-new) setup guide. Use the *TensorFlow Enterprise 2.3* no-GPU image. Leave all other settings at their default values.

After the instance is created, you can connect to [JupyterLab](https://jupyter.org/) IDE by clicking the *OPEN JUPYTERLAB* link in the [AI Platform Notebooks Console](https://console.cloud.google.com/ai-platform/notebooks/instances).

In the **JupyterLab**, open a terminal and clone this repository in the `home` folder.
```
cd
git clone https://github.com/GoogleCloudPlatform/mlops-on-gcp.git
```

From the `mlops-labs/workshops/tfx-caip-tf23` folder execute the `install.sh` script to install **TFX** and **KFP** SDKs.

```
cd mlops-on-gcp/workshops/tfx-caip-tf23
./install.sh
```

## Summary of lab exercises

### Lab-01 - TFX Components walk-through
In this lab, you will walk through  the configuration and execution of the key TFX components. The primary goal of the lab is to get a high level understanding of the function and usage of each of the components. You will work in an AI Platform Notebooks instance using the components in an interactive mode.

### Lab-02 - Orchestrating model training and deployment with TFX and Cloud AI Platform
In this lab you will develop, deploy and run a TFX pipeline that runs on Google Cloud.

### Lab-03 - CI/CD for a TFX pipeline
In this lab you will walk through authoring of a Cloud Build CI/CD workflow that automatically builds and deploys a TFX pipeline. You will also integrate your workflow with GitHub by setting up a trigger that starts the workflow when a new tag is applied to the GitHub repo hosting the pipeline's code.

### Lab-04 - ML Metadata
In this lab, you will explore ML metadata and ML artifacts created by TFX pipeline runs.
