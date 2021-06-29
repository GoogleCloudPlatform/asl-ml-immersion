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
from jax.experimental.jax2tf.examples import mnist_lib, saved_model_lib

TRAIN_BATCH_SIZE = 128
TEST_BATCH_SIZE = 16
NUM_EPOCHS = 2

# Block TF from the GPU to let JAX use it all
tf.config.set_visible_devices([], 'GPU')

logger = logging.getLogger()

# need to initialize flags somehow to avoid errors in load_mnist
flags.FLAGS([''])

flax_mnist = mnist_lib.FlaxMNIST()

train_ds = mnist_lib.load_mnist(tfds.Split.TRAIN, TRAIN_BATCH_SIZE)
test_ds = mnist_lib.load_mnist(tfds.Split.TEST, TEST_BATCH_SIZE)

image, _ = next(iter(train_ds))
input_signature = tf.TensorSpec.from_tensor(
    tf.expand_dims(image[0], axis=0)
)


def main(args):
    logger_level = logger.level
    logger.setLevel(logging.INFO)
    predict_fn, params = flax_mnist.train(
        train_ds=train_ds,
        test_ds=test_ds,
        num_epochs=NUM_EPOCHS,
    )
    logger.setLevel(logger_level)

    saved_model_lib.convert_and_save_model(
        jax_fn=predict_fn,
        params=params,
        model_dir=os.path.join(
            args["output_dir"],
            args["model_name"],
            str(args["model_version"])
        ),
        input_signatures=[input_signature],
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output_dir",
        help="GCS location to export model_version/SavedModel",
        default=os.getenv("AIP_MODEL_DIR")
    )
    parser.add_argument(
        "--model_name",
        default="model",
    )
    parser.add_argument(
        "--model_version",
        default=1,
        type=int
    )

    args = parser.parse_args().__dict__

    main(args=args)
