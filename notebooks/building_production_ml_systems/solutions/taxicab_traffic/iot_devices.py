import argparse
import datetime
import gzip
import logging
import random
import time

from google.cloud import pubsub

"""
Send sensor data to Cloud Pub/Sub in small groups, simulating real-time behavior
"""
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_TOPIC = "taxi_rides"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project", help="Google Cloud Project ID", required=True
    )
    parser.add_argument(
        "--topic",
        help="Pub/Sub Topic, will be created if doesn't exist",
        default=DEFAULT_TOPIC,
    )
    args = parser.parse_args()

    # create Pub/Sub notification topic
    logging.basicConfig(
        format="%(levelname)s: %(message)s", level=logging.INFO
    )
    publisher = pubsub.PublisherClient()
    topic_name = publisher.topic_path(args.project, args.topic)
    try:
        publisher.get_topic(topic_name)
        logging.info(f"Reusing pub/sub topic {args.topic}")
    except:
        publisher.create_topic(topic_name)
        logging.info(f"Creating pub/sub topic {args.topic}")

    while True:
        num_trips = random.randint(10, 60)
        for i in range(num_trips):
            publisher.publish(topic_name, b"taxi_ride")
        logging.info(f"Publishing: {time.ctime()}")
        time.sleep(5)
