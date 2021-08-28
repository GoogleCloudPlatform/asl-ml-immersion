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
"""TFX taxi preprocessing.

This file defines a template for TFX Transform component.
"""

from __future__ import division
from __future__ import print_function

import tensorflow as tf
import tensorflow_transform as tft

from models import features


def _fill_in_missing(x):
  """Replace missing values in a SparseTensor.

  Fills in missing values of `x` with '' or 0, and converts to a dense tensor.

  Args:
    x: A `SparseTensor` of rank 2.  Its dense shape should have size at most 1
      in the second dimension.

  Returns:
    A rank 1 tensor where missing values of `x` have been filled in.
  """
  if isinstance(x, tf.sparse.SparseTensor):
    default_value = '' if x.dtype == tf.string else 0
    dense_tensor = tf.sparse.to_dense(
        tf.SparseTensor(x.indices, x.values, [x.dense_shape[0], 1]),
        default_value)
  else:
    dense_tensor = x

  return tf.squeeze(dense_tensor, axis=1)


def preprocessing_fn(inputs):
  """tf.transform's callback function for preprocessing inputs.

  Args:
    inputs: map from feature keys to raw not-yet-transformed features.

  Returns:
    Map from string feature key to transformed feature operations.
  """
  outputs = {}
  for key in features.DENSE_FLOAT_FEATURE_KEYS:
    # Preserve this feature as a dense float, setting nan's to the mean.
    outputs[features.transformed_name(key)] = tft.scale_to_z_score(
        _fill_in_missing(inputs[key]))

  for key in features.VOCAB_FEATURE_KEYS:
    # Build a vocabulary for this feature.
    outputs[features.transformed_name(key)] = tft.compute_and_apply_vocabulary(
        _fill_in_missing(inputs[key]),
        top_k=features.VOCAB_SIZE,
        num_oov_buckets=features.OOV_SIZE)

  for key, num_buckets in zip(features.BUCKET_FEATURE_KEYS,
                              features.BUCKET_FEATURE_BUCKET_COUNT):
    outputs[features.transformed_name(key)] = tft.bucketize(
        _fill_in_missing(inputs[key]),
        num_buckets)

  for key in features.CATEGORICAL_FEATURE_KEYS:
    outputs[features.transformed_name(key)] = _fill_in_missing(inputs[key])

  # TODO(b/157064428): Support label transformation for Keras.
  # Do not apply label transformation as it will result in wrong evaluation.
  outputs[features.transformed_name(
      features.LABEL_KEY)] = inputs[features.LABEL_KEY]

  return outputs
