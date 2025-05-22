# An Example of Using Cloud Composer DAG for Vertex AI Pipelines Integration

---

This README provides an overview, setup instructions, and functionality details for an Apache Airflow DAG designed to integrate with Google Cloud's **Vertex AI Pipelines**. This DAG demonstrates a more comprehensive data preparation workflow before orchestrating the execution and management of a Kubeflow pipeline on Vertex AI.

## Purpose

The primary purpose of this DAG is to showcase a robust MLOps workflow orchestrated by **Cloud Composer (Airflow)**. Specifically, it illustrates:

1.  **Data Ingestion (GCS to BigQuery)**: Loading raw data from a Google Cloud Storage (GCS) bucket into a BigQuery table. This step emulating basic ETL pipeline orchestrated by Cloud Composer.
2.  **Data Export (BigQuery to GCS)**: Exporting processed or prepared data from BigQuery back to GCS. This is a common pattern for creating datasets ready for consumption by ML training jobs or Vertex AI Pipelines.
3.  **Vertex AI Pipeline Execution**: Triggering a pre-compiled Kubeflow Pipeline (defined in a YAML file on GCS) on **Vertex AI Pipelines**. This allows for the execution of complex machine learning workflows, including data preprocessing, model training, evaluation, and deployment, using data prepared in the preceding steps.
4.  **Pipeline Job Management**: Demonstrating how to programmatically retrieve the status of a running Vertex AI Pipeline job and subsequently delete it. This is crucial for monitoring and cleanup in automated MLOps environments.

## Setup

To set up and run this DAG, you'll need the following:

### Google Cloud Project Configuration

1.  **Enable APIs**: Ensure the following Google Cloud APIs are enabled in your project:
    * **Cloud Composer API**
    * **Vertex AI API**
    * **BigQuery API**
    * **Cloud Storage API**
2.  **Service Account Permissions**: The service account associated with your Cloud Composer environment must have the necessary permissions to:
    * Read from the specified GCS bucket (`storage.objects.get`, `storage.objects.list`).
    * Write to BigQuery (`bigquery.datasets.create`, `bigquery.tables.create`, `bigquery.tables.updateData`).
    * Read from BigQuery (`bigquery.tables.getData`, `bigquery.tables.list`).
    * Write to GCS (`storage.objects.create`, `storage.objects.delete`).
    * Run and manage Vertex AI Pipeline jobs (`aiplatform.pipelineJobs.create`, `aiplatform.pipelineJobs.get`, `aiplatform.pipelineJobs.delete`).
3.  **Cloud Composer Environment**: You need an active Cloud Composer environment (Airflow 2.x recommended).
4.  **Google Cloud Storage (GCS) Bucket**:
    * The DAG expects a GCS bucket named `asl-public` containing the source dataset `data/covertype/dataset.csv`. You can replace this with your own bucket and data.
    * You'll also need a pre-compiled Kubeflow Pipeline YAML file stored on GCS. Update the `VERTEX_AI_PIPELINE_YAML` variable in the DAG with the path to your compiled pipeline (e.g., `gs://your-bucket/path/to/covertype_kfp_pipeline.yaml`).
    * The DAG will export data to the path specified by `GCS_TRAIN_DATASET_PATH` (e.g., `gs://.../train_export.csv`). Ensure the bucket exists and the service account has write permissions.

### DAG Configuration

1.  **Update Placeholders**:
    * `PROJECT_ID`: Replace `"...project id..."` with your actual Google Cloud **Project ID**.
    * `REGION`: The region for your Vertex AI operations (e.g., `"us-central1"`).
    * `VERTEX_AI_PIPELINE_YAML`: Replace `"gs://.../covertype_kfp_pipeline.yaml"` with the actual GCS path to your compiled Kubeflow pipeline YAML file.
    * `GCS_SOURCE_DATASET_PATH` and `GCS_BUCKET_NAME`: Adjust if your source data is in a different location.
    * `GCS_TRAIN_DATASET_PATH`: Update this to your desired GCS path for the exported training data.
    * `BIGQUERY_DATASET_ID` and `TABLE_ID`: Customize these if you prefer different BigQuery dataset and table names.
2.  **Upload DAG**: Upload the DAG file (`demo_vertex_ai_pipeline_integration.py`) to the `dags` folder of your Cloud Composer environment.

### Kubeflow Pipeline (Pre-requisite)

This DAG assumes you have a pre-compiled Kubeflow Pipeline YAML file. This YAML file is typically generated from a Kubeflow Pipelines SDK definition in Python and compiled using `kfp.compiler.Compiler().compile()`. Ensure this compiled YAML is accessible at the `VERTEX_AI_PIPELINE_YAML` path specified in the DAG. The pipeline should be designed to accept `training_file_path` as a parameter.

## Functionality

The `demo_vertex_ai_pipeline_integration` DAG consists of the following tasks:

1.  **`load_csv_to_bigquery`**:
    * **Operator**: `GCSToBigQueryOperator`
    * **Purpose**: This task transfers a CSV file (`data/covertype/dataset.csv` from the `asl-public` bucket) to a specified BigQuery table (`airflow_demo_dataset.covertype`).
    * **Configuration**: It's configured to create the table if it doesn't exist and truncate it if it does, ensuring a fresh load for each run. It also handles skipping a header row.
    * **Trigger**: This is the initial task, executing first.

2.  **`bigquery_to_gcs_export`**:
    * **Operator**: `BigQueryToGCSOperator`
    * **Purpose**: This task exports the data from the BigQuery table (`airflow_demo_dataset.covertype`) to a CSV file in GCS, specified by `params.gcs_train_dataset_path`. This emulates a data preparation step where data is transformed and then made available for downstream ML processes.
    * **Trigger**: Executes once `load_csv_to_bigquery` successfully completes.

3.  **`start_vertex_ai_pipeline`**:
    * **Operator**: `RunPipelineJobOperator`
    * **Purpose**: After the data is exported to GCS, this task triggers a new **Vertex AI Pipeline** job using the specified compiled pipeline YAML file from GCS.
    * **Parameter Passing**: It passes the GCS path of the exported training data (`params.gcs_train_dataset_path`) as the `training_file_path` parameter to the Kubeflow pipeline.
    * **Dynamic Naming**: The `display_name` is dynamically generated with a timestamp to ensure uniqueness for each pipeline run.
    * **XCom**: The `pipeline_job_id` of the triggered pipeline is pushed to XCom, allowing subsequent tasks to reference this specific job.
    * **Trigger**: Executes once `bigquery_to_gcs_export` successfully completes.

4.  **`vertex_ai_pipline_status`**:
    * **Operator**: `GetPipelineJobOperator`
    * **Purpose**: This task retrieves detailed information and the current status of the Vertex AI Pipeline job initiated by the previous task. It uses the `pipeline_job_id` pulled from XCom.
    * **Trigger**: Executes once `start_vertex_ai_pipeline` successfully completes.

5.  **`delete_vertex_ai_pipeline_job`**:
    * **Operator**: `DeletePipelineJobOperator`
    * **Purpose**: This task cleans up the Vertex AI Pipeline job by deleting it. This is important for managing resources and keeping your Vertex AI environment tidy.
    * **Trigger Rule**: `TriggerRule.ALL_DONE` ensures this task runs regardless of whether the preceding tasks succeeded or failed, as long as they have all completed their execution. This is a robust approach for cleanup tasks.
    * **Trigger**: Executes once `vertex_ai_pipline_status` completes (or if any previous task fails, due to `ALL_DONE` trigger rule).

---

This DAG provides a comprehensive example for integrating your MLOps data preparation and pipeline execution workflows with Google Cloud's powerful Vertex AI platform, all orchestrated seamlessly using Cloud Composer.