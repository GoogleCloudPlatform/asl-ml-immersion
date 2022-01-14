import argparse
from datetime import datetime
import json
import time

from google.cloud import aiplatform


def convert_trainer_args(trainer_args):
    new_trainer_args = []
    for k, v in trainer_args.items():
        if isinstance(v, dict) or isinstance(v, list) or isinstance(v, tuple):
            val = json.dumps(v)
        else:
            val = v
        new_trainer_args.extend(["--" + str(k), str(val)])
    return new_trainer_args


def parse_arguments(parser):
    """Parses command line arguments.
    Args:
        parser: instance of `argparse.ArgumentParser`.
    """
    parser.add_argument(
        "--ml_framework",
        help="Which ML framework to train with.",
        type=str,
        choices=["tensorflow", "pytorch", "xgboost", "sklearn", "lightgbm", "tpot"],
        required=True
    )
    parser.add_argument(
        "--project",
        help="GCP project to train model in.",
        type=str,
        required=True
    )
    parser.add_argument(
        "--region",
        help="Region to train model in.",
        type=str,
        default="us-central1"
    )
    parser.add_argument(
        "--job_display_name",
        help="Name to give to job.",
        type=str,
        default="custom-training-{}".format(
            datetime.now().strftime("%Y%m%d%H%M%S")
        )
    )
    parser.add_argument(
        "--replica_count",
        help="Number of worker replicas to use.",
        type=int,
        default=1
    )
    parser.add_argument(
        "--pre_built_training_container_uri",
        help="URI to pre-built training container image.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--model_package_gcs_path",
        help="GCS patch where model package is stored.",
        type=str
    )
    parser.add_argument(
        "--python_module",
        help="Name of python module path.",
        type=str
    )
    parser.add_argument(
        "--custom_training_container_uri",
        help="URI to custom training container image.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--machine_type",
        help="Machine type for the workers.",
        type=str,
        default="n1-standard-4"
    )
    parser.add_argument(
        "--accelerator_type",
        help="Accelerator type.",
        type=str,
        default="ACCELERATOR_TYPE_UNSPECIFIED"
    )
    parser.add_argument(
        "--accelerator_count",
        help="Number of accelerators to use.",
        type=int,
        default=0
    )
    parser.add_argument(
        "--job_polling_frequency",
        help="Number of seconds to wait between job status polls.",
        type=int,
        default=15
    )
    parser.add_argument(
        "--trainer_args",
        help="Args used by the trainer application",
        type=json.loads,
        default=""
    )

def parse_command_line_arguments():
    """Parses command line arguments and returns dictionary.
    Returns:
        Dictionary containing command line arguments.
    """
    parser = argparse.ArgumentParser()

    # Add arguments to parser.
    parse_arguments(parser)

    # Parse all arguments.
    args = parser.parse_args()
    arguments = args.__dict__

    return arguments


def train_model(arguments):
    assert arguments["pre_built_training_container_uri"] or arguments["custom_training_container_uri"], \
    "Must use either a pre-built or custom training image."
    assert not (arguments["pre_built_training_container_uri"] and arguments["custom_training_container_uri"]), \
    "Can't use both a pre-built or custom training image."

    vertex_native_ml_frameworks = set(
        ["tensorflow", "pytorch", "xgboost", "sklearn"]
    )
    if arguments["ml_framework"] not in vertex_native_ml_frameworks:
        assert arguments["custom_training_container_uri"], \
        "Must use custom training container if using non-native Vertex AI ML framework."

    # Get accelerator_type.
    accelerator_map = {
        "NVIDIA_TESLA_K80": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80,
        "NVIDIA_TESLA_P100": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_P100,
        "NVIDIA_TESLA_V100": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_V100,
        "NVIDIA_TESLA_P4": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_P4,
        "NVIDIA_TESLA_T4": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_T4
    }
    accelerator_type = accelerator_map.get(arguments["accelerator_type"])
    if accelerator_type is None:
        accelerator_type = aiplatform.gapic.AcceleratorType.ACCELERATOR_TYPE_UNSPECIFIED

    # The AI Platform services require regional API endpoints.
    client_options = {
        "api_endpoint": "{}-aiplatform.googleapis.com".format(
            arguments["region"]
        )
    }

    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)

    machine_spec = {
        "machine_type": arguments["machine_type"],
        "accelerator_type": accelerator_type,
        "accelerator_count": arguments["accelerator_count"],
    }

    python_package_spec = {}
    if arguments["pre_built_training_container_uri"]:
        python_package_spec.update(
            {
                "executor_image_uri": arguments["pre_built_training_container_uri"],
                "package_uris": [
                    arguments["model_package_gcs_path"]
                ],
                "python_module": arguments["python_module"],
                "args": arguments["trainer_args"]
            }
        )

    container_spec = {}
    if arguments["custom_training_container_uri"]:
        container_spec.update(
            {
                "image_uri": arguments["custom_training_container_uri"],
                "args": arguments["trainer_args"]
            }
        )

    worker_pool_specs = [
        {
            "machine_spec": machine_spec,
            "replica_count": arguments["replica_count"]
        }
    ]

    for worker_pool_spec in worker_pool_specs:
        if python_package_spec:
            worker_pool_spec["python_package_spec"] = python_package_spec
        else:
            worker_pool_spec["container_spec"] = container_spec

    custom_job = {
        "display_name": arguments["job_display_name"],
        "job_spec": {
            "worker_pool_specs": worker_pool_specs,
        }
    }

    parent = "projects/{}/locations/{}".format(
        arguments["project"], arguments["region"]
    )
    response = client.create_custom_job(parent=parent, custom_job=custom_job)
    print("Response:", response)

    # Wait for job to terminate.
    running_states = set([1, 2, 3, 8])
    completed_state = 4
    while True:
        state = client.get_custom_job(name=response.name).state
        if state not in running_states:
            break
        time.sleep(arguments["job_polling_frequency"])
    assert state == completed_state, "Job did not complete successfully."


if __name__ == "__main__":
    # Parse command line arguments.
    arguments = parse_command_line_arguments()
    arguments["trainer_args"] = convert_trainer_args(
        arguments["trainer_args"]
    )
    print("arguments = {}".format(arguments))

    # Train model with configs.
    train_model(arguments)