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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf

from models import features


class FeaturesTest(tf.test.TestCase):

  def testNumberOfBucketFeatureBucketCount(self):
    self.assertEqual(
        len(features.BUCKET_FEATURE_KEYS),
        len(features.BUCKET_FEATURE_BUCKET_COUNT))
    self.assertEqual(
        len(features.CATEGORICAL_FEATURE_KEYS),
        len(features.CATEGORICAL_FEATURE_MAX_VALUES))

  def testTransformedNames(self):
    names = ["f1", "cf"]
    self.assertEqual(["f1_xf", "cf_xf"], features.transformed_names(names))


if __name__ == "__main__":
  tf.test.main()
