# Copyright 2021 Google Inc. All Rights Reserved.
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
import os.path
from typing import List, Optional

import tensorflow_model_analysis as tfma
from tfx.components import (
    CsvExampleGen,
    Evaluator,
    ExampleValidator,
    InfraValidator,
    Pusher,
    SchemaGen,
    StatisticsGen,
    Trainer,
    Transform,
)
from tfx.dsl.components.common.importer import Importer
from tfx.dsl.components.common.resolver import Resolver
from tfx.dsl.input_resolution.strategies.latest_blessed_model_strategy import (
    LatestBlessedModelStrategy,
)
from tfx.orchestration import data_types, pipeline
from tfx.proto import (
    example_gen_pb2,
    infra_validator_pb2,
    pusher_pb2,
    trainer_pb2,
)
from tfx.types import Channel
from tfx.types.standard_artifacts import Model, ModelBlessing, Schema

SCHEMA_FOLDER = "schema"
TRANSFORM_MODULE_FILE = "preprocessing.py"
TRAIN_MODULE_FILE = "model.py"
SERVING_MODEL_DIR = "serving-model"


def create_pipeline(
    pipeline_name: str,
    pipeline_root: str,
    data_root_uri: data_types.RuntimeParameter,
    train_steps: data_types.RuntimeParameter,
    eval_steps: data_types.RuntimeParameter,
    beam_pipeline_args: List[str],
    enable_cache: Optional[bool] = False,
):

    output = example_gen_pb2.Output(
        split_config=example_gen_pb2.SplitConfig(
            splits=[
                example_gen_pb2.SplitConfig.Split(name="train", hash_buckets=4),
                example_gen_pb2.SplitConfig.Split(name="eval", hash_buckets=1),
            ]
        )
    )

    examplegen = CsvExampleGen(
        input_base=data_root_uri, output_config=output
    ).with_id("CsvExampleGen")

    statisticsgen = StatisticsGen(
        examples=examplegen.outputs["examples"]
    ).with_id("StatisticsGen")

    schemagen = SchemaGen(
        statistics=statisticsgen.outputs["statistics"]
    ).with_id("SchemaGen")

    import_schema = Importer(
        source_uri=SCHEMA_FOLDER,
        artifact_type=Schema,
    ).with_id("SchemaImporter")

    examplevalidator = ExampleValidator(
        statistics=statisticsgen.outputs["statistics"],
        schema=import_schema.outputs["result"],
    ).with_id("ExampleValidator")

    transform = Transform(
        examples=examplegen.outputs["examples"],
        schema=import_schema.outputs["result"],
        module_file=TRANSFORM_MODULE_FILE,
    ).with_id("Transform")

    trainer = Trainer(
        module_file=TRAIN_MODULE_FILE,
        examples=transform.outputs["transformed_examples"],
        schema=import_schema.outputs["result"],
        transform_graph=transform.outputs["transform_graph"],
        train_args=trainer_pb2.TrainArgs(
            splits=["train"], num_steps=train_steps
        ),
        eval_args=trainer_pb2.EvalArgs(splits=["eval"], num_steps=eval_steps),
    ).with_id("Trainer")

    resolver = Resolver(
        strategy_class=LatestBlessedModelStrategy,
        model=Channel(type=Model),
        model_blessing=Channel(type=ModelBlessing),
    ).with_id("LatestBlessedModelResolver")

    accuracy_threshold = tfma.MetricThreshold(
        value_threshold=tfma.GenericValueThreshold(
            lower_bound={"value": 0.0}, upper_bound={"value": 0.99}
        ),
    )

    metrics_specs = tfma.MetricsSpec(
        metrics=[
            tfma.MetricConfig(
                class_name="SparseCategoricalAccuracy",
                threshold=accuracy_threshold,
            ),
            tfma.MetricConfig(class_name="ExampleCount"),
        ]
    )

    eval_config = tfma.EvalConfig(
        model_specs=[tfma.ModelSpec(label_key="Cover_Type")],
        metrics_specs=[metrics_specs],
        slicing_specs=[
            tfma.SlicingSpec(),
            tfma.SlicingSpec(feature_keys=["Wilderness_Area"]),
        ],
    )

    evaluator = Evaluator(
        examples=examplegen.outputs["examples"],
        model=trainer.outputs["model"],
        baseline_model=resolver.outputs["model"],
        eval_config=eval_config,
    ).with_id("ModelEvaluator")

    serving_request_spec = infra_validator_pb2.TensorFlowServingRequestSpec()
    infravalidator = InfraValidator(
        model=trainer.outputs["model"],
        examples=examplegen.outputs["examples"],
        serving_spec=infra_validator_pb2.ServingSpec(
            tensorflow_serving=infra_validator_pb2.TensorFlowServing(
                tags=["latest"]
            ),
            local_docker=infra_validator_pb2.LocalDockerConfig(),
        ),
        validation_spec=infra_validator_pb2.ValidationSpec(
            max_loading_time_seconds=60,
            num_tries=5,
        ),
        request_spec=infra_validator_pb2.RequestSpec(
            tensorflow_serving=serving_request_spec,
            num_examples=5,
        ),
    ).with_id("ModelInfraValidator")

    serving_model_dir = os.path.join(pipeline_root, SERVING_MODEL_DIR)

    pusher = Pusher(
        model=trainer.outputs["model"],
        model_blessing=evaluator.outputs["blessing"],
        infra_blessing=infravalidator.outputs["blessing"],
        push_destination=pusher_pb2.PushDestination(
            filesystem=pusher_pb2.PushDestination.Filesystem(
                base_directory=serving_model_dir
            )
        ),
    ).with_id("ModelPusher")

    components = [
        examplegen,
        statisticsgen,
        schemagen,
        import_schema,
        examplevalidator,
        transform,
        trainer,
        resolver,
        evaluator,
        infravalidator,
        pusher,
    ]

    tfx_pipeline = pipeline.Pipeline(
        pipeline_name=pipeline_name,
        pipeline_root=pipeline_root,
        components=components,
        enable_cache=enable_cache,
        beam_pipeline_args=beam_pipeline_args,
    )

    return tfx_pipeline
