import sys
from typing import Union
import pandas as pd

def get_project_id():
    import urllib.request
    url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
    req = urllib.request.Request(url)
    req.add_header("Metadata-Flavor", "Google")
    project_id = urllib.request.urlopen(req).read().decode()
    if not project_id:
        try:
            #try to retrieve PROJECT ID from config.json in gs://{PROJECT}/datagen/config.json
            config = get_local_config()
            project_id = config["project_id"]
        except:   
            try:
                import subprocess
                project_id=subprocess.check_output(["gcloud config get-value project"], shell=True).decode("utf-8").replace("\n","") 
            except:
                raise ValueError("Could not get a value for PROJECT_ID")

    return project_id

def run_bq_query(sql: str) -> Union[str, pd.DataFrame]:
    """
    Input: SQL query, as a string, to execute in BigQuery
    Returns the query results as a pandas DataFrame, or error, if any
    """
    
    from google.cloud import bigquery
    
    bq_client = bigquery.Client()
    
    # Try dry run before executing query to catch any errors
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    bq_client.query(sql, job_config=job_config)

    # If dry run succeeds without errors, proceed to run query
    job_config = bigquery.QueryJobConfig()
    client_result = bq_client.query(sql, job_config=job_config)

    job_id = client_result.job_id

    # Wait for query/job to finish running. then get & return data frame
    df = client_result.result().to_arrow().to_pandas()
    
    return df

def copy_blob(
    bucket_name, blob_name, destination_bucket_name, destination_blob_name
):
    """Copies a blob from one bucket to another with a new name."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # destination_bucket_name = "destination-bucket-name"
    # destination_blob_name = "destination-object-name"
    from google.cloud import storage
    storage_client = storage.Client()

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.bucket(destination_bucket_name)

    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name
    )

    if destination_bucket_name == "cymbal-fraudfinder":
        # make file public only if this script is being run within the cymbal-fraudfinder project
        blob_copy.make_public()
    
    print(f"File copied from gs://{source_bucket.name}/{source_blob.name} \n\t\t to gs://{destination_bucket.name}/{blob_copy.name}")


def get_batch_data_gcs(BUCKET_NAME):
    '''
    Copy necessary files for datagen streaming
    '''
    copy_blob(
        bucket_name="cymbal-fraudfinder",
        blob_name="datagen/hacked_customers_history.txt",
        destination_bucket_name=BUCKET_NAME,
        destination_blob_name="datagen/hacked_customers_history.txt"
    )

    copy_blob(
        bucket_name="cymbal-fraudfinder",
        blob_name="datagen/hacked_terminals_history.txt",
        destination_bucket_name=BUCKET_NAME,
        destination_blob_name="datagen/hacked_terminals_history.txt"
    )
    copy_blob(
        bucket_name="cymbal-fraudfinder",
        blob_name="datagen/demographics/customer_profiles.csv",
        destination_bucket_name=BUCKET_NAME,
        destination_blob_name="datagen/demographics/customer_profiles.csv"
    )

    copy_blob(
        bucket_name="cymbal-fraudfinder",
        blob_name="datagen/demographics/terminal_profiles.csv",
        destination_bucket_name=BUCKET_NAME,
        destination_blob_name="datagen/demographics/terminal_profiles.csv"
    )

    copy_blob(
        bucket_name="cymbal-fraudfinder",
        blob_name="datagen/demographics/customer_with_terminal_profiles.csv",
        destination_bucket_name=BUCKET_NAME,
        destination_blob_name="datagen/demographics/customer_with_terminal_profiles.csv"
    )

    return "Done get_batch_data_gcs"

def get_batch_data_bq(PROJECT):
    '''
    Creates the following tables in your project by copying from public tables:

    {YOUR PROJECT}
    |-`tx` (dataset)
    |-`tx` (table: transactions without labels)
    |-`txlabels` (table: transactions with fraud labels (1 or 0))
    |-demographics
    |-`customers` (table: profiles of customers)
    |-`terminals` (table: profiles of terminals)
    |-`customersterminals` (table: profiles of customers and terminals within their radius)
    '''

    run_bq_query(f"CREATE SCHEMA IF NOT EXISTS `{PROJECT}`.tx OPTIONS(location='us-central1');")
    run_bq_query(f"CREATE SCHEMA IF NOT EXISTS `{PROJECT}`.demographics OPTIONS(location='us-central1');")

    run_bq_query(f"""
    CREATE OR REPLACE TABLE `{PROJECT}`.tx.tx 
    PARTITION BY
    DATE(TX_TS)
    AS (
        SELECT
        TX_ID,
        TX_TS,
        CUSTOMER_ID,
        TERMINAL_ID,
        TX_AMOUNT
        FROM
        `cymbal-fraudfinder`.txbackup.all
    );
    """)
    print(f"BigQuery table created: `{PROJECT}`.tx.tx")

    run_bq_query(f"""
    CREATE OR REPLACE TABLE `{PROJECT}`.tx.txlabels
    AS (
        SELECT
        TX_ID,
        TX_FRAUD
        FROM
        `cymbal-fraudfinder`.txbackup.all
    );
    """)
    print(f"BigQuery table created: `{PROJECT}`.tx.txlabels")
    
    run_bq_query(f"""
    CREATE OR REPLACE TABLE `{PROJECT}`.demographics.customers
    AS (
        SELECT
        *
        FROM
        `cymbal-fraudfinder`.demographics.customers
    );
    """)
    print(f"BigQuery table created: `{PROJECT}`.demographics.customers")
    
    run_bq_query(f"""
    CREATE OR REPLACE TABLE `{PROJECT}`.demographics.terminals
    AS (
        SELECT
        *
        FROM
        `cymbal-fraudfinder`.demographics.terminals
    );
    """)
    print(f"BigQuery table created: `{PROJECT}`.demographics.terminals")
    
    run_bq_query(f"""
    CREATE OR REPLACE TABLE `{PROJECT}`.demographics.customersterminals
    AS (
        SELECT
        *
        FROM
        `cymbal-fraudfinder`.demographics.customersterminals
    );
    """)
    print(f"BigQuery table created: `{PROJECT}`.demographics.customersterminals")
    
    return "Done get_batch_data_bq"

if __name__ == "__main__":
    PROJECT = get_project_id()
    BUCKET_NAME = sys.argv[1]
    get_batch_data_gcs(BUCKET_NAME)
    get_batch_data_bq(PROJECT)