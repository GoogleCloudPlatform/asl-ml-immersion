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

from __future__ import absolute_import, division, print_function

import tensorflow as tf
from models.estimator import model
from tensorflow_metadata.proto.v0 import schema_pb2
from tfx.components.trainer import executor as trainer_executor


class ModelTest(tf.test.TestCase):
    def testTrainerFn(self):
        trainer_fn_args = trainer_executor.TrainerFnArgs(
            train_files="/path/to/train.file",
            transform_output="/path/to/transform_output",
            serving_model_dir="/path/to/model_dir",
            eval_files="/path/to/eval.file",
            schema_file="/path/to/schema_file",
            train_steps=1000,
            eval_steps=100,
        )
        schema = schema_pb2.Schema()
        result = model._create_train_and_eval_spec(
            trainer_fn_args, schema
        )  # pylint: disable=protected-access
        self.assertIsInstance(result["estimator"], tf.estimator.Estimator)
        self.assertIsInstance(result["train_spec"], tf.estimator.TrainSpec)
        self.assertIsInstance(result["eval_spec"], tf.estimator.EvalSpec)
        self.assertTrue(callable(result["eval_input_receiver_fn"]))


if __name__ == "__main__":
    tf.test.main()
