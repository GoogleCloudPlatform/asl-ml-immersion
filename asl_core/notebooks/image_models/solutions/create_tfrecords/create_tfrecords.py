# pylint: skip-file

import argparse
import random
import typing

import apache_beam as beam
import tensorflow as tf
from apache_beam.options.pipeline_options import (
    GoogleCloudOptions,
    PipelineOptions,
    SetupOptions,
    StandardOptions,
)
from apache_beam.runners import DataflowRunner, DirectRunner


# Schema of CSV file
class CSVRow(typing.NamedTuple):
    image_uri: str
    label: str


# DoFn to transform CSV rows to PCollection with schema
class ParseCsv(beam.DoFn):
    def process(self, element):
        image_uri, label = element.split(",")
        yield CSVRow(image_uri=image_uri, label=label)


# TFRecord Helper Functions
def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def _image_feature(value):
    """Returns a bytes_list from an image."""
    return tf.train.Feature(
        bytes_list=tf.train.BytesList(value=[tf.io.encode_jpeg(value).numpy()])
    )


# DoFn to create TF Example's
class CreateTFExample(beam.DoFn):
    def process(self, element):
        CLASSES = ["daisy", "dandelion", "roses", "sunflowers", "tulips"]
        img = tf.io.decode_jpeg(tf.io.read_file(element.image_uri))

        feature = {
            "image": _image_feature(img),
            "label": _int64_feature(CLASSES.index(element.label)),
        }

        yield tf.train.Example(features=tf.train.Features(feature=feature))


def partition_fn(example, num_partitions, train_percent):
    if random.random() < train_percent:
        return 0
    return 1


# Function to run the Beam pipeline
def run():
    parser = argparse.ArgumentParser(description="Image Data to TFRecords")

    # Google Cloud options
    parser.add_argument(
        "--project", required=True, help="Specify Google Cloud project"
    )
    parser.add_argument(
        "--region", required=True, help="Specify Google Cloud region"
    )
    parser.add_argument(
        "--staging_location",
        required=True,
        help="Specify Cloud Storage bucket for staging",
    )
    parser.add_argument(
        "--runner", required=True, help="Specify Apache Beam Runner"
    )
    parser.add_argument(
        "--job_name", required=True, help="Job name for Dataflow Runner"
    )

    # Pipeline-specific options
    parser.add_argument(
        "--dataset_file", required=True, help="GCS path to input CSV"
    )
    parser.add_argument(
        "--output_dir", required=True, help="GCS output directory"
    )
    parser.add_argument(
        "--train_percent", required=True, help="Percentage of training data"
    )
    parser.add_argument(
        "--requirements_file", required=True, help="Required Packages"
    )

    opts, pipeline_opts = parser.parse_known_args()

    # Setting up the Beam pipeline options.
    options = PipelineOptions(pipeline_opts)

    DATASET_FILE = opts.dataset_file
    OUTPUT_DIR = opts.output_dir
    TRAIN_PERCENT = float(opts.train_percent)

    # Set standard pipeline options.
    options.view_as(StandardOptions).streaming = False
    options.view_as(StandardOptions).runner = opts.runner
    options.view_as(SetupOptions).save_main_session = True
    options.view_as(SetupOptions).requirements_file = opts.requirements_file
    options.view_as(SetupOptions).pickle_library = "dill"

    # Set Google Cloud specific options.
    google_cloud_options = options.view_as(GoogleCloudOptions)
    google_cloud_options.project = opts.project
    google_cloud_options.job_name = opts.job_name
    google_cloud_options.staging_location = opts.staging_location
    google_cloud_options.region = opts.region

    # Instaniate pipeline
    if opts.runner == "DataflowRunner":
        p = beam.Pipeline(DataflowRunner(), options=options)
    else:
        p = beam.Pipeline(DirectRunner(), options=options)

    rows = (
        p
        | "Read CSV" >> beam.io.ReadFromText(DATASET_FILE)
        | "Parse CSV" >> beam.ParDo(ParseCsv())
    )

    train, val = (
        rows
        | "Create TF Examples" >> beam.ParDo(CreateTFExample())
        | "Split Data"
        >> beam.Partition(partition_fn, 2, train_percent=TRAIN_PERCENT)
    )

    write_train = (
        train
        | "Serialize Training Examples"
        >> beam.Map(lambda x: x.SerializeToString())
        | "Write Train"
        >> beam.io.tfrecordio.WriteToTFRecord(
            f"{OUTPUT_DIR}/train.tfrecord", num_shards=10
        )
    )
    write_val = (
        val
        | "Serialize Validation Examples"
        >> beam.Map(lambda x: x.SerializeToString())
        | "Write Validation"
        >> beam.io.tfrecordio.WriteToTFRecord(
            f"{OUTPUT_DIR}/eval.tfrecord", num_shards=3
        )
    )

    # Run pipeline
    p.run()


if __name__ == "__main__":
    run()
