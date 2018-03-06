#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import shutil
import numpy as np
import tensorflow as tf

# Set logging to be level of INFO
tf.logging.set_verbosity(tf.logging.INFO)

BUCKET = None  # set from task.py
PATTERN = 'of' # gets all files

# Determine CSV, label, and key columns
CSV_COLUMNS = 'weight_pounds,is_male,mother_age,mother_race,plurality,gestation_weeks,mother_married,cigarette_use,alcohol_use,key'.split(',')
LABEL_COLUMN = 'weight_pounds'
KEY_COLUMN = 'key'

# Set default values for each CSV column
DEFAULTS = [[0.0], ['null'], [0.0], ['null'], [0.0], [0.0], ['null'], ['null'], ['null'], ['nokey']]

# Define some hyperparameters
TRAIN_STEPS = 10000
BATCH_SIZE = 512
EMBED_SIZE = 3
HIDDEN_UNITS = [64, 16, 4]

# Create an input function reading a file using the Dataset API
# Then provide the results to the Estimator API
def read_dataset(prefix, mode, batch_size = 512):
    def _input_fn():
        def decode_csv(value_column):
            columns = tf.decode_csv(value_column, record_defaults = DEFAULTS)
            features = dict(zip(CSV_COLUMNS, columns))
            label = features.pop(LABEL_COLUMN)
            return features, label
        
        # Use prefix to create file path
        file_path = 'gs://{}/babyweight/preproc/{}*{}*'.format(BUCKET, prefix, PATTERN)

        # Create list of files that match pattern
        file_list = tf.gfile.Glob(file_path)

        # Create dataset from file list
        dataset = (tf.data.TextLineDataset(file_list)  # Read text file
                    .map(decode_csv))  # Transform each elem by applying decode_csv fn
      
        if mode == tf.estimator.ModeKeys.TRAIN:
            num_epochs = None # indefinitely
            dataset = dataset.shuffle(buffer_size = 10 * batch_size)
        else:
            num_epochs = 1 # end-of-input after this
 
        dataset = dataset.repeat(num_epochs).batch(batch_size)
        return dataset.make_one_shot_iterator().get_next()
    return _input_fn

# Define feature columns
def get_wide_deep():
    # Define column types
    races = ['White', 'Black', 'American Indian', 'Chinese', 
             'Japanese', 'Hawaiian', 'Filipino', 'Unknown',
             'Asian Indian', 'Korean', 'Samaon', 'Vietnamese']
    is_male, mother_age, mother_race, plurality, gestation_weeks, mother_married, cigarette_use, alcohol_use = \
    [ \
     tf.feature_column.categorical_column_with_vocabulary_list('is_male', 
                                                               ['True', 'False', 'Unknown']),
     tf.feature_column.numeric_column('mother_age'),
     tf.feature_column.categorical_column_with_vocabulary_list('mother_race', 
                                                               races),
     
     tf.feature_column.numeric_column('plurality'),
     tf.feature_column.numeric_column('gestation_weeks'),
     tf.feature_column.categorical_column_with_vocabulary_list('mother_married', 
                                                               ['True', 'False']),
     tf.feature_column.categorical_column_with_vocabulary_list('cigarette_use', 
                                                               ['True', 'False', 'None']),
     tf.feature_column.categorical_column_with_vocabulary_list('alcohol_use', 
                                                               ['True', 'False', 'None'])
    ]

    # Discretize/bucketize continous features
    mother_age_buckets = tf.feature_column.bucketized_column(mother_age, 
                                                             boundaries=np.arange(15, 45, 1).tolist())
    gestation_buckets = tf.feature_column.bucketized_column(gestation_weeks, 
                                                            boundaries=np.arange(17, 47, 1).tolist())

    # Feature cross all three bucketized feature columns to create a sparse representation
    buckets_crossed = tf.feature_column.crossed_column([mother_age_buckets,  
                                                        gestation_buckets], 
                                                       hash_bucket_size = 20000)

    # Embed mother race into a lower dimensional continuous space
    mother_race_embed = tf.feature_column.embedding_column(mother_race, EMBED_SIZE)

    # Sparse columns are wide, have a linear relationship with the output
    wide = [is_male, mother_race,
            mother_age_buckets, gestation_buckets,
            mother_married, cigarette_use, alcohol_use, buckets_crossed]

    # Cross all wide columns and embed into a lower dimension
    wide_crossed = tf.feature_column.crossed_column(wide, hash_bucket_size = 20000)
    wide_embed = tf.feature_column.embedding_column(wide_crossed, EMBED_SIZE)

    # Continuous columns are deep, have a complex relationship with the output
    deep = [mother_age, plurality,
            mother_race_embed,
            gestation_weeks,
            wide_embed
           ]
    return wide, deep

# Create serving input function to be able to serve predictions later using provided inputs
def serving_input_fn():
    feature_placeholders = {
      'is_male': tf.placeholder(tf.string, [None]),
      'mother_age': tf.placeholder(tf.float32, [None]),
      'mother_race': tf.placeholder(tf.string, [None]),
      'plurality': tf.placeholder(tf.float32, [None]),
      'gestation_weeks': tf.placeholder(tf.float32, [None]),
      'mother_married': tf.placeholder(tf.string, [None]),
      'cigarette_use': tf.placeholder(tf.string, [None]),
      'alcohol_use': tf.placeholder(tf.string, [None])
    }
    features = {
      key: tf.expand_dims(tensor, -1)
      for key, tensor in feature_placeholders.items()
    }
    return tf.estimator.export.ServingInputReceiver(features, feature_placeholders)

# Create estimator to train and evaluate
def train_and_evaluate(output_dir):
    wide, deep = get_wide_deep()
    estimator = tf.estimator.DNNLinearCombinedRegressor(
        model_dir = output_dir,
        linear_feature_columns = wide,
        dnn_feature_columns = deep,
        dnn_hidden_units = HIDDEN_UNITS)
    train_spec = tf.estimator.TrainSpec(
        input_fn = read_dataset(prefix = 'train.csv',
				mode = tf.estimator.ModeKeys.TRAIN,
				batch_size = BATCH_SIZE),
        max_steps = TRAIN_STEPS)
    exporter = tf.estimator.LatestExporter('exporter', serving_input_fn)
    eval_spec = tf.estimator.EvalSpec(
        input_fn = read_dataset(prefix = 'eval.csv',
				mode = tf.estimator.ModeKeys.EVAL,
				batch_size = BATCH_SIZE),
        steps = None,
        start_delay_secs = 60, # start evaluating after N seconds
        throttle_secs = 300,  # evaluate every N seconds
        exporters = exporter)
    tf.estimator.train_and_evaluate(estimator, train_spec, eval_spec)
