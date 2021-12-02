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
"""TFX template taxi model.

A tf.estimator.DNNLinearCombinedClassifier which uses features
defined in features.py and network parameters defined in constants.py.
"""


import tensorflow as tf
import tensorflow_model_analysis as tfma
import tensorflow_transform as tft
from absl import logging
from models import features
from models.estimator import constants
from tensorflow_metadata.proto.v0 import schema_pb2
from tensorflow_transform.tf_metadata import schema_utils
from tfx.utils import io_utils
from tfx_bsl.tfxio import dataset_options


def _gzip_reader_fn(filenames):
    """Small utility returning a record reader that can read gzip'ed files."""
    return tf.data.TFRecordDataset(filenames, compression_type="GZIP")


# Tf.Transform considers these features as "raw"
def _get_raw_feature_spec(schema):
    return schema_utils.schema_as_feature_spec(schema).feature_spec


def _build_estimator(config, hidden_units=None, warm_start_from=None):
    """Build an estimator for predicting the tipping behavior of taxi riders.

    Args:
      config: tf.estimator.RunConfig defining the runtime environment for the
        estimator (including model_dir).
      hidden_units: [int], the layer sizes of the DNN (input layer first)
      warm_start_from: Optional directory to warm start from.

    Returns:
      A dict of the following:
        - estimator: The estimator that will be used for training and eval.
        - train_spec: Spec for training.
        - eval_spec: Spec for eval.
        - eval_input_receiver_fn: Input function for eval.
    """
    real_valued_columns = [
        tf.feature_column.numeric_column(key, shape=())
        for key in features.transformed_names(features.DENSE_FLOAT_FEATURE_KEYS)
    ]

    categorical_columns = []
    for key in features.transformed_names(features.VOCAB_FEATURE_KEYS):
        categorical_columns.append(
            tf.feature_column.categorical_column_with_identity(
                key,
                num_buckets=features.VOCAB_SIZE + features.OOV_SIZE,
                default_value=0,
            )
        )

    for key, num_buckets in zip(
        features.transformed_names(features.BUCKET_FEATURE_KEYS),
        features.BUCKET_FEATURE_BUCKET_COUNT,
    ):
        categorical_columns.append(
            tf.feature_column.categorical_column_with_identity(
                key, num_buckets=num_buckets, default_value=0
            )
        )

    for key, num_buckets in zip(
        features.transformed_names(features.CATEGORICAL_FEATURE_KEYS),
        features.CATEGORICAL_FEATURE_MAX_VALUES,
    ):
        categorical_columns.append(
            tf.feature_column.categorical_column_with_identity(
                key, num_buckets=num_buckets, default_value=0
            )
        )

    return tf.estimator.DNNLinearCombinedClassifier(
        config=config,
        linear_feature_columns=categorical_columns,
        dnn_feature_columns=real_valued_columns,
        dnn_hidden_units=hidden_units or [100, 70, 50, 25],
        warm_start_from=warm_start_from,
    )


def _example_serving_receiver_fn(tf_transform_output, schema):
    """Build the serving in inputs.

    Args:
      tf_transform_output: A TFTransformOutput.
      schema: the schema of the input data.

    Returns:
      Tensorflow graph which parses examples, applying tf-transform to them.
    """
    raw_feature_spec = _get_raw_feature_spec(schema)
    raw_feature_spec.pop(features.LABEL_KEY)

    raw_input_fn = tf.estimator.export.build_parsing_serving_input_receiver_fn(
        raw_feature_spec, default_batch_size=None
    )
    serving_input_receiver = raw_input_fn()

    transformed_features = tf_transform_output.transform_raw_features(
        serving_input_receiver.features
    )

    return tf.estimator.export.ServingInputReceiver(
        transformed_features, serving_input_receiver.receiver_tensors
    )


def _eval_input_receiver_fn(tf_transform_output, schema):
    """Build everything needed for the tf-model-analysis to run the model.

    Args:
      tf_transform_output: A TFTransformOutput.
      schema: the schema of the input data.

    Returns:
      EvalInputReceiver function, which contains:
        - Tensorflow graph which parses raw untransformed features, applies the
          tf-transform preprocessing operators.
        - Set of raw, untransformed features.
        - Label against which predictions will be compared.
    """
    # Notice that the inputs are raw features, not transformed features here.
    raw_feature_spec = _get_raw_feature_spec(schema)

    serialized_tf_example = tf.compat.v1.placeholder(
        dtype=tf.string, shape=[None], name="input_example_tensor"
    )

    # Add a parse_example operator to the tensorflow graph, which will parse
    # raw, untransformed, tf examples.
    raw_features = tf.io.parse_example(
        serialized=serialized_tf_example, features=raw_feature_spec
    )

    # Now that we have our raw examples, process them through the tf-transform
    # function computed during the preprocessing step.
    transformed_features = tf_transform_output.transform_raw_features(
        raw_features
    )

    # The key name MUST be 'examples'.
    receiver_tensors = {"examples": serialized_tf_example}

    # NOTE: Model is driven by transformed features (since training works on the
    # materialized output of TFT, but slicing will happen on raw features.
    raw_features.update(transformed_features)

    return tfma.export.EvalInputReceiver(
        features=raw_features,
        receiver_tensors=receiver_tensors,
        labels=transformed_features[
            features.transformed_name(features.LABEL_KEY)
        ],
    )


def _input_fn(file_pattern, data_accessor, tf_transform_output, batch_size=200):
    """Generates features and label for tuning/training.

    Args:
      file_pattern: List of paths or patterns of input tfrecord files.
      data_accessor: DataAccessor for converting input to RecordBatch.
      tf_transform_output: A TFTransformOutput.
      batch_size: representing the number of consecutive elements of returned
        dataset to combine in a single batch

    Returns:
      A dataset that contains (features, indices) tuple where features is a
        dictionary of Tensors, and indices is a single Tensor of label indices.
    """
    return data_accessor.tf_dataset_factory(
        file_pattern,
        dataset_options.TensorFlowDatasetOptions(
            batch_size=batch_size,
            label_key=features.transformed_name(features.LABEL_KEY),
        ),
        tf_transform_output.transformed_metadata.schema,
    )


def _create_train_and_eval_spec(trainer_fn_args, schema):
    """Build the estimator using the high level API.

    Args:
      trainer_fn_args: Holds args used to train the model as name/value pairs.
      schema: Holds the schema of the training examples.

    Returns:
      A dict of the following:
        - estimator: The estimator that will be used for training and eval.
        - train_spec: Spec for training.
        - eval_spec: Spec for eval.
        - eval_input_receiver_fn: Input function for eval.
    """

    tf_transform_output = tft.TFTransformOutput(
        trainer_fn_args.transform_output
    )

    train_input_fn = lambda: _input_fn(  # pylint: disable=g-long-lambda
        trainer_fn_args.train_files,
        trainer_fn_args.data_accessor,
        tf_transform_output,
        batch_size=constants.TRAIN_BATCH_SIZE,
    )

    eval_input_fn = lambda: _input_fn(  # pylint: disable=g-long-lambda
        trainer_fn_args.eval_files,
        trainer_fn_args.data_accessor,
        tf_transform_output,
        batch_size=constants.EVAL_BATCH_SIZE,
    )

    train_spec = tf.estimator.TrainSpec(  # pylint: disable=g-long-lambda
        train_input_fn, max_steps=trainer_fn_args.train_steps
    )

    serving_receiver_fn = (
        lambda: _example_serving_receiver_fn(  # pylint: disable=g-long-lambda
            tf_transform_output, schema
        )
    )

    exporter = tf.estimator.FinalExporter("chicago-taxi", serving_receiver_fn)
    eval_spec = tf.estimator.EvalSpec(
        eval_input_fn,
        steps=trainer_fn_args.eval_steps,
        exporters=[exporter],
        name="chicago-taxi-eval",
    )

    run_config = tf.estimator.RunConfig(
        save_checkpoints_steps=999, keep_checkpoint_max=1
    )

    run_config = run_config.replace(model_dir=trainer_fn_args.serving_model_dir)

    estimator = _build_estimator(
        hidden_units=constants.HIDDEN_UNITS, config=run_config
    )

    # Create an input receiver for TFMA processing
    receiver_fn = (
        lambda: _eval_input_receiver_fn(  # pylint: disable=g-long-lambda
            tf_transform_output, schema
        )
    )

    return {
        "estimator": estimator,
        "train_spec": train_spec,
        "eval_spec": eval_spec,
        "eval_input_receiver_fn": receiver_fn,
    }


# TFX will call this function
def run_fn(fn_args):
    """Train the model based on given args.

    Args:
      fn_args: Holds args used to train the model as name/value pairs.
    """
    schema = io_utils.parse_pbtxt_file(fn_args.schema_file, schema_pb2.Schema())

    train_and_eval_spec = _create_train_and_eval_spec(fn_args, schema)

    # Train the model
    logging.info("Training model.")
    tf.estimator.train_and_evaluate(
        train_and_eval_spec["estimator"],
        train_and_eval_spec["train_spec"],
        train_and_eval_spec["eval_spec"],
    )
    logging.info(
        "Training complete.  Model written to %s", fn_args.serving_model_dir
    )

    # Export an eval savedmodel for TFMA
    # NOTE: When trained in distributed training cluster, eval_savedmodel must
    # be exported only by the chief worker.
    logging.info("Exporting eval_savedmodel for TFMA.")
    tfma.export.export_eval_savedmodel(
        estimator=train_and_eval_spec["estimator"],
        export_dir_base=fn_args.eval_model_dir,
        eval_input_receiver_fn=train_and_eval_spec["eval_input_receiver_fn"],
    )

    logging.info("Exported eval_savedmodel to %s.", fn_args.eval_model_dir)
