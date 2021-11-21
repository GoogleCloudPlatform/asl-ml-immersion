# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Transform some training data from a public BigQuery dataset into CSV files
in Cloud Storage.
"""

import argparse
import os

from google import api_core
from google.cloud import bigquery
from google.cloud.bigquery.job import ExtractJobConfig

DATASET = "taxifare"
TRAIN_TABLE = "feateng_training_data"
VALID_TABLE = "feateng_valid_data"

TRAIN_SQL = """ CREATE OR REPLACE TABLE taxifare.feateng_training_data AS

SELECT
    (tolls_amount + fare_amount) AS fare_amount,
    pickup_datetime,
    pickup_longitude AS pickuplon,
    pickup_latitude AS pickuplat,
    dropoff_longitude AS dropofflon,
    dropoff_latitude AS dropofflat,
    passenger_count*1.0 AS passengers,
    'unused' AS key
FROM `nyc-tlc.yellow.trips`
WHERE ABS(MOD(FARM_FINGERPRINT(CAST(pickup_datetime AS STRING)), 1000)) = 1
AND
    trip_distance > 0
    AND fare_amount >= 2.5
    AND pickup_longitude > -78
    AND pickup_longitude < -70
    AND dropoff_longitude > -78
    AND dropoff_longitude < -70
    AND pickup_latitude > 37
    AND pickup_latitude < 45
    AND dropoff_latitude > 37
    AND dropoff_latitude < 45
    AND passenger_count > 0
"""

VALID_SQL = """
CREATE OR REPLACE TABLE taxifare.feateng_valid_data AS

SELECT
    (tolls_amount + fare_amount) AS fare_amount,
    pickup_datetime,
    pickup_longitude AS pickuplon,
    pickup_latitude AS pickuplat,
    dropoff_longitude AS dropofflon,
    dropoff_latitude AS dropofflat,
    passenger_count*1.0 AS passengers,
    'unused' AS key
FROM `nyc-tlc.yellow.trips`
WHERE ABS(MOD(FARM_FINGERPRINT(CAST(pickup_datetime AS STRING)), 10000)) = 2
AND
    trip_distance > 0
    AND fare_amount >= 2.5
    AND pickup_longitude > -78
    AND pickup_longitude < -70
    AND dropoff_longitude > -78
    AND dropoff_longitude < -70
    AND pickup_latitude > 37
    AND pickup_latitude < 45
    AND dropoff_latitude > 37
    AND dropoff_latitude < 45
    AND passenger_count > 0
"""


def export_table_to_gcs(bq_client, dataset_ref, source_table, destination_uri):
    table_ref = dataset_ref.table(source_table)

    config = ExtractJobConfig()
    config.print_header = False

    extract_job = bq_client.extract_table(
        table_ref,
        destination_uri,
        location="US",
        job_config=config,
    )
    extract_job.result()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bucket",
        help="GCS bucket where datasets will be exported.",
        required=True,
    )
    args = parser.parse_args()

    gs_prefix = "gs://"
    bucket = (
        args.bucket
        if gs_prefix in args.bucket
        else os.path.join(gs_prefix, args.bucket)
    )
    datadir = os.path.join(bucket, DATASET, "data")
    train_export_path = os.path.join(datadir, "taxi-train-*.csv")
    valid_export_path = os.path.join(datadir, "taxi-valid-*.csv")

    bq_client = bigquery.Client()

    dataset_ref = bigquery.Dataset(bq_client.dataset("taxifare"))

    try:
        bq_client.create_dataset(dataset_ref)
        print("Dataset created")
    except api_core.exceptions.Conflict:
        print("Dataset already exists")

    print("Creating the training dataset...")
    bq_client.query(TRAIN_SQL).result()

    print("Creating the validation dataset...")
    bq_client.query(VALID_SQL).result()

    print("Exporting training dataset to GCS", train_export_path)
    export_table_to_gcs(bq_client, dataset_ref, TRAIN_TABLE, train_export_path)

    print("Exporting validation dataset to GCS", valid_export_path)
    export_table_to_gcs(bq_client, dataset_ref, VALID_TABLE, valid_export_path)


if __name__ == "__main__":
    main()
