import argparse

from google.cloud import aiplatform


def parse_arguments(parser):
    """Parses command line arguments.
    Args:
        parser: instance of `argparse.ArgumentParser`.
    """
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
        "--endpoint_display_name",
        help="Name of endpoint to deploy model to.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--endpoint_id",
        help="Previously created endpoint ID to deploy model to.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--model_display_name",
        help="Name of Vertex AI uploaded model to deploy to endpoint.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--model_id",
        help="Previously created model ID to use.",
        type=str,
        default=""
    )
    parser.add_argument(
        "--deployed_model_display_name",
        help="Name to display for deployed model.",
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


def deploy_model(arguments):
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

    # Initialize.
    aiplatform.init(
        project=arguments["project"], location=arguments["region"]
    )

    # First create endpoint.
    endpoint_id = arguments["endpoint_id"]
    if not endpoint_id:
        endpoint_display_name = arguments["endpoint_display_name"]
        endpoint_name_match = aiplatform.Endpoint.list(
            filter="display_name={}".format(endpoint_display_name)
        )
        if endpoint_name_match:
            print(
                "Endpoint with name {} already exists!".format(
                    endpoint_display_name
                )
            )
            endpoint_display_name = "{}_0".format(endpoint_display_name)

        endpoint = aiplatform.Endpoint.create(
            display_name=endpoint_display_name
        )
        endpoint_id = endpoint.resource_name.split("/")[-1]
    else:
        # Fetch Endpoint object.
        endpoint = aiplatform.Endpoint(endpoint_name=model_id)
    print("Endpoint ID = {}".format(endpoint_id))

    # Get model ID.
    model_id = arguments["model_id"]
    if not model_id:
        model_display_name = arguments["model_display_name"]
        model_name_match = aiplatform.Model.list(
            filter="display_name={}".format(model_display_name)
        )
        if not model_name_match:
            print(
                "Model with name {} does NOT exist!".format(
                    model_display_name
                )
            )
            return
        else:
            model_id = model_name_match[0].name.split("/")[-1]
    print("Model ID = {}".format(model_id))

    # Fetch Model object.
    model = aiplatform.Model(model_name=model_id)

    # Deploy model to endpoint.
    deployed_model_display_name = arguments["deployed_model_display_name"]
    deployed_model_list = endpoint.list_models()
    for deployed_model in deployed_model_list:
        if deployed_model.display_name == deployed_model_display_name:
            print(
                "Deployed model with name {} already exists!".format(
                    deployed_model_display_name
                )
            )
            deployed_model_display_name = "{}_0".format(
                deployed_model_display_name
            )
        break
    response = model.deploy(
        endpoint=endpoint,
        deployed_model_display_name=deployed_model_display_name,
        machine_type=arguments["machine_type"],
        accelerator_type=accelerator_type,
        accelerator_count=arguments["accelerator_count"],
        sync=True
    )
    deployed_model_id = response.name.split("/")[-1]
    print("Deployed model ID = {}".format(deployed_model_id))


if __name__ == "__main__":
    arguments = parse_command_line_arguments()
    deploy_model(arguments)