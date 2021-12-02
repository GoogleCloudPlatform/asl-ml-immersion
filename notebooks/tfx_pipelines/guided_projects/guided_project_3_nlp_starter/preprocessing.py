# Copyright 2021 Google LLC. All Rights Reserved.
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
"""Preprocessing."""


import tensorflow as tf
from config import FEATURE_KEY, LABEL_KEY, transformed_name


def _fill_in_missing(x):
    default_value = "" if x.dtype == tf.string else 0
    return tf.squeeze(
        tf.sparse.to_dense(
            tf.SparseTensor(x.indices, x.values, [x.dense_shape[0], 1]),
            default_value,
        ),
        axis=1,
    )


def preprocessing_fn(inputs):
    features = _fill_in_missing(inputs[FEATURE_KEY])
    labels = _fill_in_missing(inputs[LABEL_KEY])
    return {
        transformed_name(FEATURE_KEY): features,
        transformed_name(LABEL_KEY): labels,
    }
