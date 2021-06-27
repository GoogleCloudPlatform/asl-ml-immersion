# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import logging
import os

import tensorflow as tf
import tensorflow_datasets as tfds
from absl import flags
from jax.experimental.jax2tf.examples.mnist_lib import (
    load_mnist, FlaxMNIST
)
# from jax.experimental.jax2tf.examples.saved_model_lib import (
#     convert_and_save_model
# )

from trainer.saved_model_lib_tf2_4 import convert_and_save_model

TRAIN_BATCH_SIZE = 128
TEST_BATCH_SIZE = 16
NUM_EPOCHS = 2

# Block TF from the GPU to let JAX use it all
tf.config.set_visible_devices([], 'GPU')

logger = logging.getLogger()

# need to initialize flags somehow to avoid errors in load_mnist
flags.FLAGS(['e'])

flax_mnist = FlaxMNIST()

train_ds = load_mnist(tfds.Split.TRAIN, TRAIN_BATCH_SIZE)
test_ds = load_mnist(tfds.Split.TEST, TEST_BATCH_SIZE)

image, _ = next(iter(train_ds))
input_signature = tf.TensorSpec.from_tensor(
    tf.expand_dims(image[0], axis=0)
)


def main(output_dir):
    logger_level = logger.level
    logger.setLevel(logging.INFO)
    predict_fn, params = flax_mnist.train(
        train_ds=train_ds,
        test_ds=test_ds,
        num_epochs=NUM_EPOCHS,
    )
    logger.setLevel(logger_level)

    convert_and_save_model(
        jax_fn=predict_fn,
        params=params,
        model_dir=output_dir,
        input_signatures=[input_signature],
        enable_xla=False,
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        help="GCS location to export SavedModel",
        default=os.getenv("AIP_MODEL_DIR")
    )
    args = parser.parse_args().__dict__

    main(output_dir=args["output_dir"])
