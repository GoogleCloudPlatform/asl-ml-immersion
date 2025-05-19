"""Ae example of using Cloud Composer DAG for VertexAI Pipelines integration"""
import datetime

from airflow import DAG
from airflow.utils.trigger_rule import TriggerRule
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.operators.vertex_ai.pipeline_job import (
    DeletePipelineJobOperator,
    GetPipelineJobOperator,
    ListPipelineJobOperator,
    RunPipelineJobOperator,
)

# Replace with your actual project and region
PROJECT_ID = "project id" # Put your project id here
REGION = "us-central1"
GCS_PIPELINE_PATH = "gs://us-central1...pipeline.yaml" # Put your compiled kubeflow pipeline yaml

GCS_SOURCE_DATASET_PATH = "data/covertype/dataset.csv"
GCS_BUCKET_NAME = "asl-public"

BIGQUERY_DATASET_ID = "airflow_demo_dataset"
BIGQUERY_TABLE_ID = "covertype"

BIGQUERY_TABLE_SCHEMA = [
    {"name": "Elevation", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Aspect", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Slope", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Horizontal_Distance_To_Hydrology", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Vertical_Distance_To_Hydrology", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Horizontal_Distance_To_Roadways", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Hillshade_9am", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Hillshade_Noon", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Hillshade_3pm", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Horizontal_Distance_To_Fire_Points", "type": "INTEGER", "mode": "NULLABLE"},
    {"name": "Wilderness_Area", "type": "STRING", "mode": "NULLABLE"},
    {"name": "Soil_Type", "type": "STRING", "mode": "NULLABLE"},
    {"name": "Cover_Type", "type": "INTEGER", "mode": "NULLABLE"}
],

with DAG(
        dag_id="trigger_vertex_ai_pipeline",
        start_date=datetime.datetime(2025, 1, 1),
        schedule=None,
        catchup=False,
        tags=["vertex_ai", "pipeline", "ml"],
        params={
        },
) as dag:
    # Loading dataset from GCS to BigQuery
    load_gcs_to_bigquery = GCSToBigQueryOperator(
        task_id="load_csv_to_bigquery",
        bucket=GCS_BUCKET_NAME,
        source_objects=[GCS_SOURCE_DATASET_PATH],
        destination_project_dataset_table=f"{BIGQUERY_DATASET_ID}.{BIGQUERY_TABLE_ID}",
        schema_fields=BIGQUERY_TABLE_SCHEMA,  # Optional: Define schema, remove if auto-detect works for you
        source_format="CSV",  # Or "NEWLINE_DELIMITED_JSON", "PARQUET", "AVRO", etc.
        create_disposition="CREATE_IF_NEEDED",  # Creates the table if it doesn't exist
        write_disposition="WRITE_TRUNCATE",  # Overwrites the table if it exists. Use "WRITE_APPEND" to append.
        skip_leading_rows=1,  # For CSVs with a header row
        field_delimiter=",",  # For CSVs
    )
    # Triggering a pipeline from a GCS compiled yaml file
    run_vertex_ai_pipeline = RunPipelineJobOperator(
        task_id="start_vertex_ai_pipeline",
        project_id=PROJECT_ID,
        region=REGION,
        template_path=GCS_PIPELINE_PATH,
        parameter_values={
            # "data_path": "{{ params.data_input_path }}",  # example of passing params to kubeflow pipeline
        },
        display_name="triggered-demo-pipeline-{{ ts_nodash }}",  # Unique display name
    )

    # Fetching VertexAI pipeline job information
    get_vertexai_ai_pipline_status = GetPipelineJobOperator(
        task_id="vertex_ai_pipline_status",
        project_id=PROJECT_ID,
        region=REGION,
        pipeline_job_id="{{ task_instance.xcom_pull(task_ids='start_vertex_ai_pipeline_from_gcs', key='pipeline_job_id') }}"
    )

    # Deleting VertexAI pipeline job
    delete_pipeline_job = DeletePipelineJobOperator(
        task_id="delete_vertex_ai_pipeline_job",
        project_id=PROJECT_ID,
        region=REGION,
        pipeline_job_id="{{ task_instance.xcom_pull(task_ids='start_vertex_ai_pipeline_from_gcs', key='pipeline_job_id') }}",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # Combine all steps as a DAG
    load_gcs_to_bigquery >> run_vertex_ai_pipeline >> get_vertexai_ai_pipline_status >> delete_pipeline_job
