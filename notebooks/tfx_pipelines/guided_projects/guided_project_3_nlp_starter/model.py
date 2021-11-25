import tensorflow as tf
import tensorflow_transform as tft
from config import (
    EVAL_BATCH_SIZE,
    HUB_DIM,
    HUB_URL,
    LABEL_KEY,
    MODEL_NAME,
    N_CLASSES,
    N_NEURONS,
    TRAIN_BATCH_SIZE,
    transformed_name,
)
from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.layers import Dense
from tensorflow.keras.models import Sequential
from tensorflow_hub import KerasLayer
from tfx_bsl.tfxio import dataset_options


def _get_serve_tf_examples_fn(model, tf_transform_output):
    model.tft_layer = tf_transform_output.transform_features_layer()

    @tf.function
    def serve_tf_examples_fn(serialized_tf_examples):
        """Returns the output to be used in the serving signature."""
        feature_spec = tf_transform_output.raw_feature_spec()
        feature_spec.pop(LABEL_KEY)
        parsed_features = tf.io.parse_example(serialized_tf_examples, feature_spec)
        transformed_features = model.tft_layer(parsed_features)
        return model(transformed_features)

    return serve_tf_examples_fn


def _input_fn(file_pattern, data_accessor, tf_transform_output, batch_size=200):
    return data_accessor.tf_dataset_factory(
        file_pattern,
        dataset_options.TensorFlowDatasetOptions(
            batch_size=batch_size,
            label_key=transformed_name(LABEL_KEY)),
        tf_transform_output.transformed_metadata.schema
    )


def _load_hub_module_layer():
    hub_module = KerasLayer(
        HUB_URL, output_shape=[HUB_DIM],
        input_shape=[], dtype=tf.string, trainable=True)
    return hub_module


def _build_keras_model():
    hub_module = _load_hub_module_layer()
    model = Sequential([
        hub_module,
        Dense(N_NEURONS, activation='relu'),
        Dense(N_CLASSES, activation='softmax')
    ])
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=[tf.keras.metrics.SparseCategoricalAccuracy()]
    )
    return model



def run_fn(fn_args):

    tf_transform_output = tft.TFTransformOutput(fn_args.transform_output)

    train_dataset = _input_fn(fn_args.train_files, fn_args.data_accessor,
                            tf_transform_output, TRAIN_BATCH_SIZE)

    eval_dataset = _input_fn(fn_args.eval_files, fn_args.data_accessor,
                           tf_transform_output, EVAL_BATCH_SIZE)

    mirrored_strategy = tf.distribute.MirroredStrategy()

    with mirrored_strategy.scope():
        model = _build_keras_model()

    tensorboard_callback = tf.keras.callbacks.TensorBoard(
        log_dir=fn_args.model_run_dir, update_freq='batch')

    model.fit(
        train_dataset,
        steps_per_epoch=fn_args.train_steps,
        validation_data=eval_dataset,
        validation_steps=fn_args.eval_steps,
        callbacks=[tensorboard_callback])

    signatures = {
        'serving_default':
            _get_serve_tf_examples_fn(model,
                                   tf_transform_output).get_concrete_function(
                                        tf.TensorSpec(
                                            shape=[None],
                                            dtype=tf.string,
                                            name='examples')),
    }
    model.save(fn_args.serving_model_dir, save_format='tf', signatures=signatures)
