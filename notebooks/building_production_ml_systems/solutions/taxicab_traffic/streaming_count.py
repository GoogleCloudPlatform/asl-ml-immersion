"""A streaming dataflow pipeline to count pub/sub messages.
"""


import argparse
import logging
from datetime import datetime

import apache_beam as beam
from apache_beam.options.pipeline_options import (
    GoogleCloudOptions,
    PipelineOptions,
    SetupOptions,
    StandardOptions,
)
from apache_beam.transforms import window  # pylint: disable=unused-import


class CountFn(beam.CombineFn):
    """Counter function to accumulate statistics"""

    def create_accumulator(self):
        return 0

    def add_input(
        self, count, input
    ):  # pylint: disable=redefined-builtin,unused-argument
        return count + 1

    def merge_accumulators(self, accumulators):
        return sum(accumulators)

    def extract_output(self, count):
        return count


def run(argv=None):
    """Build and run the pipeline."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--project", help=("Google Cloud Project ID"), required=True
    )
    parser.add_argument("--region", help=("Google Cloud region"), required=True)
    parser.add_argument(
        "--input_topic",
        help=("Google Cloud PubSub topic name "),
        required=True,
    )

    known_args, pipeline_args = parser.parse_known_args(argv)

    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    pipeline_options.view_as(StandardOptions).streaming = True
    pipeline_options.view_as(GoogleCloudOptions).region = known_args.region
    pipeline_options.view_as(GoogleCloudOptions).project = known_args.project

    p = beam.Pipeline(options=pipeline_options)

    topic = f"projects/{known_args.project}/topics/{known_args.input_topic}"
    # this table needs to exist
    table_spec = f"{known_args.project}:taxifare.traffic_realtime"

    def to_bq_format(count):
        """BigQuery writer requires rows to be stored as python dictionary"""
        return {
            "trips_last_5min": count,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    pipeline = (  # noqa F841 pylint: disable=unused-variable
        p
        | "read_from_pubsub"
        >> beam.io.ReadFromPubSub(topic=topic).with_output_types(bytes)
        | "window"
        >> beam.WindowInto(window.SlidingWindows(size=300, period=15))
        | "count" >> beam.CombineGlobally(CountFn()).without_defaults()
        | "format_for_bq" >> beam.Map(to_bq_format)
        | "write_to_bq"
        >> beam.io.WriteToBigQuery(
            table_spec,
            # WRITE_TRUNCATE not supported for streaming
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
            create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
        )
    )

    result = p.run()  # noqa F841 pylint: disable=unused-variable
    # result.wait_until_finish() #only do this if running with DirectRunner


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()
