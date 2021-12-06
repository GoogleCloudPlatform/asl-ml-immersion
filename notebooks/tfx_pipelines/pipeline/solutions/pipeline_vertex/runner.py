# Copyright 2021 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""TFX runner configuration"""
from tfx.orchestration.kubeflow.v2 import kubeflow_v2_dag_runner

from config import Config
from pipeline import create_pipeline



if __name__ == "__main__":

    tfx_pipeline = create_pipeline(
        pipeline_name=Config.PIPELINE_NAME,
        pipeline_root=Config.PIPELINE_ROOT,
        data_root_uri=Config.DATA_ROOT,
        train_steps=Config.TRAIN_STEPS,
        eval_steps=Config.EVAL_STEPS,
    )
    
    runner = kubeflow_v2_dag_runner.KubeflowV2DagRunner(
        config=kubeflow_v2_dag_runner.KubeflowV2DagRunnerConfig(
            default_image=Config.TFX_IMAGE
        ),
        output_filename=Config.PIPELINE_JSON,
    )
    
    runner.run(tfx_pipeline, write_out=True)
