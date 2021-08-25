# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Covertype training pipeline DSL."""

import os
from typing import Dict, List, Optional, Text

import features
import kfp
import tensorflow_model_analysis as tfma
from tfx.components import (CsvExampleGen, Evaluator, ExampleValidator,
                            ImporterNode, InfraValidator, Pusher, ResolverNode,
                            SchemaGen, StatisticsGen, Trainer, Transform)
from tfx.components.base import executor_spec
from tfx.components.trainer import executor as trainer_executor
from tfx.dsl.experimental import latest_blessed_model_resolver
from tfx.extensions.google_cloud_ai_platform.pusher import \
    executor as ai_platform_pusher_executor
from tfx.extensions.google_cloud_ai_platform.trainer import \
    executor as ai_platform_trainer_executor
from tfx.orchestration import data_types, pipeline
from tfx.orchestration.kubeflow import kubeflow_dag_runner
from tfx.orchestration.kubeflow.proto import kubeflow_pb2
from tfx.proto import (evaluator_pb2, example_gen_pb2, infra_validator_pb2,
                       pusher_pb2, trainer_pb2)
from tfx.types import Channel
from tfx.types.standard_artifacts import (InfraBlessing, Model, ModelBlessing,
                                          Schema)
from tfx.utils.dsl_utils import external_input

SCHEMA_FOLDER='schema'
TRANSFORM_MODULE_FILE='preprocessing.py'
TRAIN_MODULE_FILE='model.py'


def create_pipeline(pipeline_name: Text,
                      pipeline_root: Text,
                      data_root_uri: data_types.RuntimeParameter,
                      train_steps: data_types.RuntimeParameter,
                      eval_steps: data_types.RuntimeParameter,
                      ai_platform_training_args: Dict[Text, Text],
                      ai_platform_serving_args: Dict[Text, Text],
                      beam_pipeline_args: List[Text],
                      enable_cache: Optional[bool] = False) -> pipeline.Pipeline:
  """Trains and deploys the Covertype classifier."""


  # Brings data into the pipeline and splits the data into training and eval splits
  examples = external_input(data_root_uri)
  output_config = example_gen_pb2.Output(
    split_config=example_gen_pb2.SplitConfig(splits=[
        example_gen_pb2.SplitConfig.Split(name='train', hash_buckets=4),
        example_gen_pb2.SplitConfig.Split(name='eval', hash_buckets=1)
    ]))
  generate_examples = # TODO

  # Computes statistics over data for visualization and example validation.
  generate_statistics = # TODO

  # Import a user-provided schema
  import_schema = ImporterNode(
      instance_name='import_user_schema',
      source_uri=SCHEMA_FOLDER,
      artifact_type=Schema)

  # Generates schema based on statistics files.Even though, we use user-provided schema
  # we still want to generate the schema of the newest data for tracking and comparison
  infer_schema = # TODO

  # Performs anomaly detection based on statistics and data schema.
  validate_stats = # TODO

  # Performs transformations and feature engineering in training and serving.
  transform = # TODO


  # Trains the model using a user provided trainer function.
  train = Trainer(
      custom_executor_spec=executor_spec.ExecutorClassSpec(
          ai_platform_trainer_executor.GenericExecutor),
#      custom_executor_spec=executor_spec.ExecutorClassSpec(trainer_executor.GenericExecutor),
      module_file=TRAIN_MODULE_FILE,
      transformed_examples=transform.outputs.transformed_examples,
      schema=import_schema.outputs.result,
      transform_graph=transform.outputs.transform_graph,
      train_args={'num_steps': train_steps},
      eval_args={'num_steps': eval_steps},
      custom_config={'ai_platform_training_args': ai_platform_training_args})

  # Get the latest blessed model for model validation.
  resolve = ResolverNode(
      instance_name='latest_blessed_model_resolver',
      resolver_class=latest_blessed_model_resolver.LatestBlessedModelResolver,
      model=Channel(type=Model),
      model_blessing=Channel(type=ModelBlessing))

  # Uses TFMA to compute a evaluation statistics over features of a model.
  accuracy_threshold = tfma.MetricThreshold(
                value_threshold=tfma.GenericValueThreshold(
                    lower_bound={'value': 0.5},
                    upper_bound={'value': 0.99}),
                change_threshold=tfma.GenericChangeThreshold(
                    absolute={'value': 0.0001},
                    direction=tfma.MetricDirection.HIGHER_IS_BETTER),
                )

  metrics_specs = tfma.MetricsSpec(
                   metrics = [
                       tfma.MetricConfig(class_name='SparseCategoricalAccuracy',
                           threshold=accuracy_threshold),
                       tfma.MetricConfig(class_name='ExampleCount')])

  eval_config = tfma.EvalConfig(
    model_specs=[
        tfma.ModelSpec(label_key='Cover_Type')
    ],
    metrics_specs=[metrics_specs],
    slicing_specs=[
        tfma.SlicingSpec(),
        tfma.SlicingSpec(feature_keys=['Wilderness_Area'])
    ]
  )


  analyze = Evaluator(
      examples=generate_examples.outputs.examples,
      model=train.outputs.model,
      baseline_model=resolve.outputs.model,
      eval_config=eval_config
  )

  # Validate model can be loaded and queried in sand-boxed environment
  # mirroring production.
  serving_config = infra_validator_pb2.ServingSpec(
      tensorflow_serving=infra_validator_pb2.TensorFlowServing(
          tags=['latest']),
      kubernetes=infra_validator_pb2.KubernetesConfig(),
  )

  validation_config = infra_validator_pb2.ValidationSpec(
      max_loading_time_seconds=60,
      num_tries=3,
  )

  request_config = infra_validator_pb2.RequestSpec(
      tensorflow_serving=infra_validator_pb2.TensorFlowServingRequestSpec(),
      num_examples=3,
  )

  infra_validate = InfraValidator(
      model=train.outputs['model'],
      examples=generate_examples.outputs['examples'],
      serving_spec=serving_config,
      validation_spec=validation_config,
      request_spec=request_config,
  )

  # Checks whether the model passed the validation steps and pushes the model
  # to a file destination if check passed.
  deploy = Pusher(
      custom_executor_spec=executor_spec.ExecutorClassSpec(ai_platform_pusher_executor.Executor),
      model=train.outputs['model'],
      model_blessing=analyze.outputs['blessing'],
      infra_blessing=infra_validate.outputs['blessing'],
      custom_config={ai_platform_pusher_executor.SERVING_ARGS_KEY: ai_platform_serving_args})

  #TODO: Create and return a Pipeline object using `pipeline_name` as name, `pipeline_root` as root,
  # as well as all the component you defined above. Make sure to pass the correct `beam_pipline_args` and
  # please enbable cache.
