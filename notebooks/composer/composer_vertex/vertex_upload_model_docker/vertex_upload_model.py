import argparse

from google.cloud import aiplatform


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
        help="GCP project to deploy model to.",
        type=str,
        required=True
    )
    parser.add_argument(
        "--region",
        help="Region to deploy model in.",
        type=str,
        default="us-central1"
    )
    parser.add_argument(
        "--model_display_name",
        help="Name of model to upload trained model to.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--serving_container_image_uri",
        help="URI of serving container image.",
        type=str,
        default="us-docker.pkg.dev/vertex-ai/prediction/tf2-cpu.2-5:latest"
    )
    parser.add_argument(
        "--artifact_uri",
        help="GCS path URI where trained model is stored.",
        type=str,
        required=True
    )
    parser.add_argument(
        "--custom_serving_container_health_route",
        help="HTTP path on the container to send health checks to.",
        type=str,
        default="/health"
    )
    parser.add_argument(
        "--custom_serving_container_predict_route",
        help="HTTP path on the container to send prediction requests to.",
        type=str,
        default="/predict"
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


def upload_model(arguments):
    vertex_native_ml_frameworks = set(
        ["tensorflow", "pytorch", "xgboost", "sklearn"]
    )
    if arguments["ml_framework"] not in vertex_native_ml_frameworks:
        prebuilt_prefixes = set(
            [
                "us-docker.pkg.dev/vertex-ai/prediction",
                "europe-docker.pkg.dev/vertex-ai/prediction",
                "asia-docker.pkg.dev/vertex-ai/prediction"
            ]
        )
        uri_prefix = "/".join(
            arguments["serving_container_image_uri"].split("/")[:3]
        )
        
        assert uri_prefix not in prebuilt_prefixes, \
        "Must use custom prediction container if using non-native Vertex AI ML framework."

    # Initialize.
    aiplatform.init(
        project=arguments["project"], location=arguments["region"]
    )

    # Next upload model.
    model_display_name = arguments["model_display_name"]
    model_name_match = aiplatform.Model.list(
        filter="display_name={}".format(model_display_name)
    )
    if model_name_match:
        print(
            "Model with name {} already exists!".format(
                model_display_name
            )
        )
        model_display_name = "{}_0".format(model_display_name)

    if arguments["ml_framework"] in vertex_native_ml_frameworks:
        response = aiplatform.Model.upload(
            display_name=model_display_name,
            serving_container_image_uri=arguments["serving_container_image_uri"],
            artifact_uri=arguments["artifact_uri"]
        )
    else:
        response = aiplatform.Model.upload(
            display_name=model_display_name,
            serving_container_image_uri=arguments["serving_container_image_uri"],
            serving_container_predict_route=arguments["custom_serving_container_predict_route"],
            serving_container_health_route=arguments["custom_serving_container_health_route"],
            artifact_uri=arguments["artifact_uri"]
        )
    model_id = response.name.split("/")[-1]
    print("Model ID = {}".format(model_id))


if __name__ == "__main__":
    arguments = parse_command_line_arguments()
    upload_model(arguments)