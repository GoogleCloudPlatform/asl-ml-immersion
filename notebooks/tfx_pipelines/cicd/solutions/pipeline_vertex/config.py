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
"""The pipeline configurations.
"""

import os


class Config:
    """Sets configuration vars."""

    PROJECT_ID = os.getenv("PROJECT_ID")
    REGION = os.getenv("REGION", "us-central1")
    ARTIFACT_STORE = os.getenv("ARTIFACT_STORE", f"gs://{PROJECT_ID}")
    PIPELINE_NAME = os.getenv("PIPELINE_NAME", "tfxcovertype")

    _DATA_ROOT_DEFAULT = f"gs://{PROJECT_ID}/data/{PIPELINE_NAME}"
    DATA_ROOT_URI = os.getenv("DATA_ROOT_URI", _DATA_ROOT_DEFAULT)

    _TFX_IMAGE_DEFAULT = f"gcr.io/{PROJECT_ID}/{PIPELINE_NAME}"
    TFX_IMAGE_URI = os.getenv("TFX_IMAGE_URI", _TFX_IMAGE_DEFAULT)

    PIPELINE_JSON = os.getenv("PIPELINE_JSON", f"{PIPELINE_NAME}.json")
    PIPELINE_ROOT = os.path.join(ARTIFACT_STORE, PIPELINE_NAME)

    BEAM_DIRECT_PIPELINE_ARGS = [
        f"--project={PROJECT_ID}",
        f"--temp_location={os.path.join(PIPELINE_ROOT, 'beam')}",  # pylint: disable=inconsistent-quotes
        f"--region={REGION}",
        "--runner=DataflowRunner",
        "--experiments=use_runner_v2",
    ]

    ENABLE_CACHE = bool(os.getenv("ENABLE_CACHE", "False"))

    TRAIN_STEPS = int(os.getenv("TRAIN_STEPS", "2"))
    EVAL_STEPS = int(os.getenv("EVAL_STEPS", "1"))
    TRAIN_SPLIT = int(os.getenv("TRAIN_SPLIT", "4"))
    EVAL_SPLIT = int(os.getenv("EVAL_SPLIT", "1"))
    PUSH_LOWER_BOUND = float(os.getenv("PUSH_LOWER_BOUND", "0.0"))
    PUSH_UPPER_BOUND = float(os.getenv("PUSH_UPPER_BOUND", "1.0"))
