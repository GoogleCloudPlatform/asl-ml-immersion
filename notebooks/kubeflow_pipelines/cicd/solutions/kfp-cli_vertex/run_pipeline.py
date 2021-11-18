# Copyright 2021 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this
# file except in compliance with the License. You may obtain a copy of the License at

# https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
"""Run a compiled Kubeflow pipeline on Vertex AI."""
import fire
from google.cloud import aiplatform


def run_pipeline(project_id, region, template_path, display_name):

    aiplatform.init(project=project_id, location=region)

    pipeline = aiplatform.PipelineJob(
        display_name=display_name,
        template_path=template_path,
        enable_caching=False,
    )

    pipeline.run()

if __name__ == '__main__':
    fire.Fire(run_pipeline)
