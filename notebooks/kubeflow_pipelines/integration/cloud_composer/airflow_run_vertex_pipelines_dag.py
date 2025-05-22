"""Ae example of using Cloud Composer DAG for VertexAI Pipelines integration"""

import datetime

from airflow import DAG
from airflow.providers.google.cloud.operators.vertex_ai.pipeline_job import (
    DeletePipelineJobOperator,
    GetPipelineJobOperator,
    RunPipelineJobOperator,
)
from airflow.providers.google.cloud.transfers.bigquery_to_gcs import (
    BigQueryToGCSOperator,
)
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import (
    GCSToBigQueryOperator,
)
from airflow.utils.trigger_rule import TriggerRule

# Replace with your actual project and region
# Put your project id here
PROJECT_ID = "...project id..."
REGION = "us-central1"

# Put path to a compiled kubeflow pipeline yaml
VERTEX_AI_PIPELINE_YAML = "gs://.../covertype_kfp_pipeline.yaml"

GCS_SOURCE_DATASET_PATH = "data/covertype/dataset.csv"
GCS_BUCKET_NAME = "asl-public"

GCS_TRAIN_DATASET_PATH = ("gs://.../train_export.csv",)

# Put your BigQuery dataset id here:
BIGQUERY_DATASET_ID = "airflow_demo_dataset"
TABLE_ID = "covertype"

BIGQUERY_TABLE_SCHEMA = (
    [
        {"name": "Elevation", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "Aspect", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "Slope", "type": "INTEGER", "mode": "NULLABLE"},
        {
            "name": "Horizontal_Distance_To_Hydrology",
            "type": "INTEGER",
            "mode": "NULLABLE",
        },
        {
            "name": "Vertical_Distance_To_Hydrology",
            "type": "INTEGER",
            "mode": "NULLABLE",
        },
        {
            "name": "Horizontal_Distance_To_Roadways",
            "type": "INTEGER",
            "mode": "NULLABLE",
        },
        {"name": "Hillshade_9am", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "Hillshade_Noon", "type": "INTEGER", "mode": "NULLABLE"},
        {"name": "Hillshade_3pm", "type": "INTEGER", "mode": "NULLABLE"},
        {
            "name": "Horizontal_Distance_To_Fire_Points",
            "type": "INTEGER",
            "mode": "NULLABLE",
        },
        {"name": "Wilderness_Area", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Soil_Type", "type": "STRING", "mode": "NULLABLE"},
        {"name": "Cover_Type", "type": "INTEGER", "mode": "NULLABLE"},
    ],
)

with DAG(
    dag_id="demo_vertex_ai_pipeline_integration",
    start_date=datetime.datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
    tags=["vertex_ai", "pipeline", "ml"],
    params={
        # Put path to an exported train dataset
        "gcs_train_dataset_path": GCS_TRAIN_DATASET_PATH,
    },
) as dag:

    # Loading dataset from GCS to BigQuery (Emulating basic ETL process)
    load_gcs_to_bigquery = GCSToBigQueryOperator(
        task_id="load_csv_to_bigquery",
        bucket=GCS_BUCKET_NAME,
        source_objects=[GCS_SOURCE_DATASET_PATH],
        destination_project_dataset_table=f"{BIGQUERY_DATASET_ID}.{TABLE_ID}",
        # Optional: Define schema, remove if auto-detect works for you
        schema_fields=BIGQUERY_TABLE_SCHEMA,
        # Or "NEWLINE_DELIMITED_JSON", "PARQUET", "AVRO", etc.
        source_format="CSV",
        # Creates the table if it doesn't exist
        create_disposition="CREATE_IF_NEEDED",
        # Overwrites the table if it exists. Use "WRITE_APPEND" to append.
        write_disposition="WRITE_TRUNCATE",
        skip_leading_rows=1,  # For CSVs with a header row
        field_delimiter=",",  # For CSVs
    )

    # exporting dataset from BigQuery to GCS
    bigquery_to_gcs = BigQueryToGCSOperator(
        task_id="bigquery_to_gcs_export",
        source_project_dataset_table=f"{BIGQUERY_DATASET_ID}.{TABLE_ID}",
        destination_cloud_storage_uris="{{ params.gcs_train_dataset_path }}",
        export_format="CSV",
        print_header=True,
    )

    # Triggering a pipeline from a GCS compiled yaml file
    run_vertex_ai_pipeline = RunPipelineJobOperator(
        task_id="start_vertex_ai_pipeline",
        project_id=PROJECT_ID,
        region=REGION,
        template_path=VERTEX_AI_PIPELINE_YAML,
        # example of passing params to kubeflow pipeline
        parameter_values={
            "training_file_path": "{{ params.gcs_train_dataset_path }}",
        },
        # Unique display name
        display_name="triggered-demo-pipeline-{{ ts_nodash }}",
    )

    # Fetching VertexAI pipeline job information
    get_vertexai_ai_pipline_status = GetPipelineJobOperator(
        task_id="vertex_ai_pipline_status",
        project_id=PROJECT_ID,
        region=REGION,
        pipeline_job_id="{{ task_instance.xcom_pull("
        "task_ids='start_vertex_ai_pipeline', "
        "key='pipeline_job_id') }}",
    )

    # Deleting VertexAI pipeline job
    delete_pipeline_job = DeletePipelineJobOperator(
        task_id="delete_vertex_ai_pipeline_job",
        project_id=PROJECT_ID,
        region=REGION,
        pipeline_job_id="{{ task_instance.xcom_pull("
        "task_ids='start_vertex_ai_pipeline', "
        "key='pipeline_job_id') }}",
        trigger_rule=TriggerRule.ALL_DONE,
    )

    # Combine all steps into a DAG
    # fmt: on
    (  # pylint: disable=line-too-long, pointless-statement
        load_gcs_to_bigquery  # pylint: disable=line-too-long, pointless-statement
        >> bigquery_to_gcs  # pylint: disable=line-too-long, pointless-statement
        >> run_vertex_ai_pipeline  # pylint: disable=line-too-long, pointless-statement
        >> get_vertexai_ai_pipline_status  # pylint: disable=line-too-long, pointless-statement
        >> delete_pipeline_job  # pylint: disable=line-too-long, pointless-statement
    )  # pylint: disable=line-too-long, pointless-statement
    # fmt: off
