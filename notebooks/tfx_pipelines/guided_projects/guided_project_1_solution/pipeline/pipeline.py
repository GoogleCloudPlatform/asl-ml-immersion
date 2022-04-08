# Lint as: python2, python3
# Copyright 2020 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TFX taxi template pipeline definition.

This file defines TFX pipeline and various components in the pipeline.
"""


from typing import Any, Dict, List, Optional

import tensorflow_model_analysis as tfma
from ml_metadata.proto import metadata_store_pb2
from tfx.components import CsvExampleGen  # pylint: disable=unused-import
from tfx.components import (
    Evaluator,
    ExampleValidator,
    Pusher,
    ResolverNode,
    SchemaGen,
    StatisticsGen,
    Trainer,
    Transform,
)
from tfx.components.trainer import executor as trainer_executor
from tfx.dsl.components.base import executor_spec
from tfx.dsl.experimental import latest_blessed_model_resolver
from tfx.extensions.google_cloud_ai_platform.pusher import (
    executor as ai_platform_pusher_executor,
)
from tfx.extensions.google_cloud_ai_platform.trainer import (
    executor as ai_platform_trainer_executor,
)
from tfx.extensions.google_cloud_big_query.example_gen import (
    component as big_query_example_gen_component,  # pylint: disable=unused-import
)
from tfx.orchestration import pipeline
from tfx.proto import pusher_pb2, trainer_pb2
from tfx.types import Channel
from tfx.types.standard_artifacts import Model, ModelBlessing


def create_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    data_path: str,  # pylint: disable=unused-argument
    # TODO(step 7): (Optional) Uncomment here to use BigQuery as a data source.
    query: str,
    preprocessing_fn: str,
    run_fn: str,
    train_args: trainer_pb2.TrainArgs,
    eval_args: trainer_pb2.EvalArgs,
    eval_accuracy_threshold: float,
    serving_model_dir: str,
    metadata_connection_config: Optional[
        metadata_store_pb2.ConnectionConfig
    ] = None,
    beam_pipeline_args: Optional[List[str]] = None,
    ai_platform_training_args: Optional[Dict[str, str]] = None,
    ai_platform_serving_args: Optional[Dict[str, Any]] = None,
) -> pipeline.Pipeline:
    """Implements the chicago taxi pipeline with TFX."""

    components = []

    # Brings data into the pipeline or otherwise joins/converts training data.
    # example_gen = CsvExampleGen(input=external_input(data_path))
    # TODO(step 7): (Optional) Uncomment here to use BigQuery as a data source.
    example_gen = big_query_example_gen_component.BigQueryExampleGen(
        query=query
    )
    components.append(example_gen)

    # Computes statistics over data for visualization and example validation.
    statistics_gen = StatisticsGen(examples=example_gen.outputs["examples"])
    # TODO(step 5): Uncomment here to add StatisticsGen to the pipeline.
    components.append(statistics_gen)

    # Generates schema based on statistics files.
    schema_gen = SchemaGen(
        statistics=statistics_gen.outputs["statistics"],
        infer_feature_shape=True,
    )
    # TODO(step 5): Uncomment here to add SchemaGen to the pipeline.
    components.append(schema_gen)

    # Performs anomaly detection based on statistics and data schema.
    example_validator = ExampleValidator(  # pylint: disable=unused-variable
        statistics=statistics_gen.outputs["statistics"],
        schema=schema_gen.outputs["schema"],
    )
    # TODO(step 5): Uncomment here to add ExampleValidator to the pipeline.
    components.append(example_validator)

    # Performs transformations and feature engineering in training and serving.
    transform = Transform(
        examples=example_gen.outputs["examples"],
        schema=schema_gen.outputs["schema"],
        preprocessing_fn=preprocessing_fn,
    )
    # TODO(step 6): Uncomment here to add Transform to the pipeline.
    components.append(transform)

    # Uses user-provided Python function that implements a model using TF-Learn.
    trainer_args = {
        "run_fn": run_fn,
        "transformed_examples": transform.outputs["transformed_examples"],
        "schema": schema_gen.outputs["schema"],
        "transform_graph": transform.outputs["transform_graph"],
        "train_args": train_args,
        "eval_args": eval_args,
        "custom_executor_spec": executor_spec.ExecutorClassSpec(
            trainer_executor.GenericExecutor
        ),
    }
    if ai_platform_training_args is not None:
        trainer_args.update(
            {
                "custom_executor_spec": executor_spec.ExecutorClassSpec(
                    ai_platform_trainer_executor.GenericExecutor
                ),
                "custom_config": {
                    # pylint: disable-next=line-too-long
                    ai_platform_trainer_executor.TRAINING_ARGS_KEY: ai_platform_training_args,
                },
            }
        )
    trainer = Trainer(**trainer_args)
    # TODO(step 6): Uncomment here to add Trainer to the pipeline.
    components.append(trainer)

    # Get the latest blessed model for model validation.
    model_resolver = ResolverNode(
        instance_name="latest_blessed_model_resolver",
        resolver_class=latest_blessed_model_resolver.LatestBlessedModelResolver,
        model=Channel(type=Model),
        model_blessing=Channel(type=ModelBlessing),
    )
    # TODO(step 6): Uncomment here to add ResolverNode to the pipeline.
    components.append(model_resolver)

    # Uses TFMA to compute a evaluation statistics over features of a model and
    # perform quality validation of a candidate model (compared to a baseline).
    eval_config = tfma.EvalConfig(
        model_specs=[tfma.ModelSpec(label_key="big_tipper")],
        slicing_specs=[tfma.SlicingSpec()],
        metrics_specs=[
            tfma.MetricsSpec(
                metrics=[
                    tfma.MetricConfig(
                        class_name="BinaryAccuracy",
                        threshold=tfma.MetricThreshold(
                            value_threshold=tfma.GenericValueThreshold(
                                lower_bound={"value": eval_accuracy_threshold}
                            ),
                            change_threshold=tfma.GenericChangeThreshold(
                                direction=tfma.MetricDirection.HIGHER_IS_BETTER,
                                absolute={"value": -1e-10},
                            ),
                        ),
                    )
                ]
            )
        ],
    )
    evaluator = Evaluator(
        examples=example_gen.outputs["examples"],
        model=trainer.outputs["model"],
        baseline_model=model_resolver.outputs["model"],
        # Change threshold will be ignored if there is no baseline (first run).
        eval_config=eval_config,
    )
    # TODO(step 6): Uncomment here to add Evaluator to the pipeline.
    components.append(evaluator)

    # Checks whether the model passed the validation steps and pushes the model
    # to a file destination if check passed.
    pusher_args = {
        "model": trainer.outputs["model"],
        "model_blessing": evaluator.outputs["blessing"],
        "push_destination": pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(
                base_directory=serving_model_dir
            )
        ),
    }
    if ai_platform_serving_args is not None:
        pusher_args.update(
            {
                "custom_executor_spec": executor_spec.ExecutorClassSpec(
                    ai_platform_pusher_executor.Executor
                ),
                "custom_config": {
                    # pylint: disable-next=line-too-long
                    ai_platform_pusher_executor.SERVING_ARGS_KEY: ai_platform_serving_args
                },
            }
        )
    pusher = Pusher(**pusher_args)  # pylint: disable=unused-variable
    # TODO(step 6): Uncomment here to add Pusher to the pipeline.
    components.append(pusher)

    return pipeline.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        # Change this value to control caching of execution results. Default
        # value is `False`.
        enable_cache=False,
        metadata_connection_config=metadata_connection_config,
        beam_pipeline_args=beam_pipeline_args,
    )
