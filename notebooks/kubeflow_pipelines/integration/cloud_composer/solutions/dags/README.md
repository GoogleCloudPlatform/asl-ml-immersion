---
# Cloud Composer DAG for Vertex AI Pipelines Integration

This README provides a description and instructions for the `demo_vertex_ai_pipeline_integration` DAG.
This DAG provides a robust example of integrating Cloud Composer with Vertex AI for automated MLOps workflows.
It demonstrates a common MLOps workflow on Google Cloud, leveraging **Cloud Composer** (managed Apache Airflow) 
to orchestrate data loading, transformation, and the execution of a **Vertex AI Pipeline**.

---

## Overview

The `demo_vertex_ai_pipeline_integration` DAG performs the following steps:

1.  **Load Data to BigQuery**: Downloads a CSV dataset from Google Cloud Storage (GCS) and loads it into a BigQuery table. This emulates an ETL (Extract, Transform, Load) process for preparing data.
2.  **Export Data from BigQuery to GCS**: Exports the processed data from BigQuery back to GCS. This step prepares the data in a format suitable for consumption by a Vertex AI Pipeline.
3.  **Run Vertex AI Pipeline**: Triggers a pre-compiled Kubeflow Pipeline (KFP) on Vertex AI using a YAML file stored in GCS. This pipeline can encapsulate various machine learning tasks like training, evaluation, and deployment.
4.  **Get Vertex AI Pipeline Status**: Retrieves the status and details of the running Vertex AI Pipeline job.
5.  **Delete Vertex AI Pipeline Job**: Cleans up by deleting the Vertex AI Pipeline job, regardless of its completion status.

---

## Prerequisites

Before deploying and running this DAG, ensure you have the following:

* A **Google Cloud Project** with billing enabled.
* A **Cloud Composer environment** provisioned in your GCP project.
* **Vertex AI API** enabled in your GCP project.
* **BigQuery API** enabled in your GCP project.
* A GCS bucket (`asl-public` in this example) containing the source dataset (`data/covertype/dataset.csv`).
* A compiled Kubeflow Pipeline YAML file uploaded to a GCS bucket (e.g., `gs://your-bucket/covertype_kfp_pipeline.yaml`). This file defines the steps of your Vertex AI Pipeline.

---

## Setup and Configuration

1.  **Update Placeholders**:
    Open the DAG file (`demo_vertex_ai_pipeline_integration.py`) and replace the placeholder values with your specific project details:

    * `PROJECT_ID`: Replace `"...project id..."` with your actual Google Cloud Project ID.
    * `VERTEX_AI_PIPELINE_YAML`: Replace `gs://.../covertype_kfp_pipeline.yaml` with the GCS path to your compiled Kubeflow Pipeline YAML file.
    * `GCS_TRAIN_DATASET_PATH`: Update `gs://.../train_export.csv` to the desired GCS path for the exported training data.
    * `BIGQUERY_DATASET_ID`: Replace `airflow_demo_dataset` with the ID of your BigQuery dataset. If it doesn't exist, it will be created by the DAG.

    ```python
    # Replace with your actual project and region
    # Put your project id here
    PROJECT_ID = "your-gcp-project-id" # e.g., "my-ml-project-12345"
    REGION = "us-central1" # Or your desired region

    # Put path to a compiled kubeflow pipeline yaml
    VERTEX_AI_PIPELINE_YAML = "gs://your-bucket/path/to/your_kfp_pipeline.yaml"

    GCS_SOURCE_DATASET_PATH = "data/covertype/dataset.csv" # Keep as is or change if your source data path is different
    GCS_BUCKET_NAME = "asl-public" # Keep as is or change if your source data is in a different bucket

    GCS_TRAIN_DATASET_PATH = ("gs://your-bucket/path/to/train_export.csv",)

    # Put your BigQuery dataset id here:
    BIGQUERY_DATASET_ID = "your_airflow_demo_dataset" # e.g., "ml_data_warehouse"
    TABLE_ID = "covertype"
    ```

2.  **Ensure IAM Permissions**:
    The service account associated with your Cloud Composer environment must have the necessary IAM roles to:
    * Read from and write to **BigQuery**.
    * Read from and write to **Cloud Storage**.
    * Create, run, and manage **Vertex AI Pipeline Jobs**.

    Recommended roles include:
    * `BigQuery Data Editor`
    * `Storage Object Admin`
    * `Vertex AI User`

---

## Deployment

1.  **Upload the DAG**:
    Upload the `demo_vertex_ai_pipeline_integration.py` file to the `dags` folder in your Cloud Composer environment's GCS bucket. Once uploaded, Airflow will automatically detect and parse the DAG.

---

## Running the DAG

You can trigger the DAG manually from the Airflow UI:

1.  Navigate to your Cloud Composer environment in the Google Cloud Console.
2.  Click on the "Airflow UI" link.
3.  In the Airflow UI, find the `demo_vertex_ai_pipeline_integration` DAG.
4.  Toggle the DAG to "On" if it's not already.
5.  Click the "Trigger DAG" button.

You can also schedule the DAG by uncommenting and configuring the `schedule_interval` parameter in the DAG definition.

---

## Monitoring

Monitor the DAG run from the Airflow UI. You can view the status of each task, logs, and XCom values. For Vertex AI Pipeline job details, you can refer to the Vertex AI section in the Google Cloud Console.

---

## Key Components

* **`GCSToBigQueryOperator`**: Facilitates loading data from GCS into BigQuery.
* **`BigQueryToGCSOperator`**: Enables exporting data from BigQuery to GCS.
* **`RunPipelineJobOperator`**: The core operator for triggering and running a Vertex AI Pipeline from a compiled YAML file. It also allows passing parameters to the pipeline.
* **`GetPipelineJobOperator`**: Used to retrieve information about a specific Vertex AI Pipeline job.
* **`DeletePipelineJobOperator`**: Cleans up Vertex AI Pipeline jobs. The `trigger_rule=TriggerRule.ALL_DONE` ensures this task runs even if previous tasks fail, ensuring proper cleanup.

---
