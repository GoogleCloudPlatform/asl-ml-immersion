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

import tensorflow_model_analysis as tfma
from config import Config
from tfx.dsl.components.common.importer import Importer
from tfx.dsl.components.common.resolver import Resolver
from tfx.dsl.input_resolution.strategies.latest_blessed_model_strategy import (
    LatestBlessedModelStrategy,
)
from tfx.orchestration import data_types, pipeline
from tfx.proto import example_gen_pb2, pusher_pb2, trainer_pb2
from tfx.types import Channel
from tfx.types.standard_artifacts import Model, ModelBlessing, Schema
from tfx.v1.components import (
    CsvExampleGen,
    Evaluator,
    ExampleValidator,
    Pusher,
    SchemaGen,
    StatisticsGen,
    Trainer,
    Transform,
)

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
):

    beam_pipeline_args = Config.BEAM_DIRECT_PIPELINE_ARGS

    output = example_gen_pb2.Output(
        split_config=example_gen_pb2.SplitConfig(
            splits=[
                example_gen_pb2.SplitConfig.Split(
                    name="train", hash_buckets=Config.TRAIN_SPLIT
                ),
                example_gen_pb2.SplitConfig.Split(
                    name="eval", hash_buckets=Config.EVAL_SPLIT
                ),
            ]
        )
    )

    examplegen = #TODO

    statisticsgen = #TODO

    schemagen = #TODO

    import_schema = Importer(
        source_uri=SCHEMA_FOLDER,
        artifact_type=Schema,
    ).with_id("SchemaImporter")

    examplevalidator = #TODO

    transform = Transform(
        examples=examplegen.outputs["examples"],
        schema=import_schema.outputs["result"],
        module_file=TRANSFORM_MODULE_FILE,
        force_tf_compat_v1=True,
    ).with_id("Transform")

    trainer = #TODO

    resolver = Resolver(
        strategy_class=LatestBlessedModelStrategy,
        model=Channel(type=Model),
        model_blessing=Channel(type=ModelBlessing),
    ).with_id("LatestBlessedModelResolver")

    accuracy_threshold = tfma.MetricThreshold(
        value_threshold=tfma.GenericValueThreshold(
            lower_bound={"value": Config.PUSH_LOWER_BOUND},
            upper_bound={"value": Config.PUSH_UPPER_BOUND},
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

    evaluator = #TODO

    serving_model_dir = os.path.join(pipeline_root, SERVING_MODEL_DIR)

    pusher = Pusher(
        model=trainer.outputs["model"],
        model_blessing=evaluator.outputs["blessing"],
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
        pusher,
    ]

    tfx_pipeline = pipeline.Pipeline(# TODO)

    return tfx_pipeline
