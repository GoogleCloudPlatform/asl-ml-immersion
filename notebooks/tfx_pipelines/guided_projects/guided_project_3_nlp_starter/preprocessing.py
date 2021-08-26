import tensorflow as tf

from config import (
    LABEL_KEY,
    N_CLASSES,
    FEATURE_KEY,
    transformed_name
)

def _fill_in_missing(x):
    default_value = '' if x.dtype == tf.string else 0
    return tf.squeeze(
        tf.sparse.to_dense(
            tf.SparseTensor(x.indices, x.values, [x.dense_shape[0], 1]),
            default_value),
        axis=1)


def preprocessing_fn(inputs):
    features = _fill_in_missing(inputs[FEATURE_KEY])
    labels =  _fill_in_missing(inputs[LABEL_KEY])
    return {
        transformed_name(FEATURE_KEY): features,
        transformed_name(LABEL_KEY): labels
    }
