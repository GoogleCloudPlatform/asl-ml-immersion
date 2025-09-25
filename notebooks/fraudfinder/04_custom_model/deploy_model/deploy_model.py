import argparse
import os
import sys
import logging
import json
print("=========== model deployment =============")
from google.cloud import aiplatform as vertex_ai
print("=========== model deployment =============")


SCRIPT_DIR = os.path.dirname(
    os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__)))
)
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, "..")))

SERVING_SPEC_FILEPATH = 'deploy_model/serving_resources_spec.json'

def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--mode', 
        type=str,
    )

    parser.add_argument(
        '--project',  
        type=str,
    )
    
    parser.add_argument(
        '--region',  
        type=str,
    )
    
    parser.add_argument(
        '--endpoint-display-name', 
        type=str,
    )

    parser.add_argument(
        '--model-display-name', 
        type=str,
    )
    
    parser.add_argument(
        '--pipeline-name', 
        type=str,
    )
    
    parser.add_argument(
        '--pipelines-store', 
        type=str,
    )

    return parser.parse_args()


def create_endpoint(project, region, endpoint_display_name):
    logging.info(f"Creating endpoint {endpoint_display_name}")
    vertex_ai.init(
        project=project,
        location=region
    )
    
    endpoints = vertex_ai.Endpoint.list(
        filter=f'display_name={endpoint_display_name}', 
        order_by="update_time")
    
    if len(endpoints) > 0:
        logging.info(f"Endpoint {endpoint_display_name} already exists.")
        endpoint = endpoints[-1]
    else:
        endpoint = vertex_ai.Endpoint.create(endpoint_display_name)
    logging.info(f"Endpoint is ready.")
    logging.info(endpoint.gca_resource)
    return endpoint


def deploy_model(project, region, endpoint_display_name, model_display_name, serving_resources_spec):
    logging.info(f"Deploying model {model_display_name} to endpoint {endpoint_display_name}")
    vertex_ai.init(
        project=project,
        location=region
    )
    
    model = vertex_ai.Model.list(
        filter=f'display_name={model_display_name}',
        order_by="update_time"
    )[-1]
    
    endpoint = vertex_ai.Endpoint.list(
        filter=f'display_name={endpoint_display_name}',
        order_by="update_time"
    )[-1]

    deployed_model = endpoint.deploy(model=model, **serving_resources_spec)
    logging.info(f"Model is deployed.")
    logging.info(deployed_model)
    return deployed_model


def compile_pipeline(pipeline_name):
    from src.tfx_pipelines import runner
    pipeline_definition_file = f"{pipeline_name}.json"
    pipeline_definition = runner.compile_training_pipeline(pipeline_definition_file)
    return pipeline_definition

    

def main():
    args = get_args()
    
    if args.mode == 'create-endpoint':
        if not args.project:
            raise ValueError("project must be supplied.")
        if not args.region:
            raise ValueError("region must be supplied.")
        if not args.endpoint_display_name:
            raise ValueError("endpoint_display_name must be supplied.")
            
        result = create_endpoint(
            args.project, 
            args.region, 
            args.endpoint_display_name
        )
        
    elif args.mode == 'deploy-model':
        if not args.project:
            raise ValueError("project must be supplied.")
        if not args.region:
            raise ValueError("region must be supplied.")
        if not args.endpoint_display_name:
            raise ValueError("endpoint-display-name must be supplied.")
        if not args.model_display_name:
            raise ValueError("model-display-name must be supplied.")
            
        with open(SERVING_SPEC_FILEPATH) as json_file:
            serving_resources_spec = json.load(json_file)
        logging.info(f"serving resources: {serving_resources_spec}")
        result = deploy_model(
            args.project, 
            args.region, 
            args.endpoint_display_name, 
            args.model_display_name,
            serving_resources_spec
        )
        
    elif args.mode == 'compile-pipeline':
        if not args.pipeline_name:
            raise ValueError("pipeline-name must be supplied.")
            
        result = compile_pipeline(args.pipeline_name)

    else:
        raise ValueError(f"Invalid mode {args.mode}.")
        
    logging.info(result)


if __name__ == "__main__":
    main()

