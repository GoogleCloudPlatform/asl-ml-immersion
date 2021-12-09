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
"""Helper function to deploy a Vertex pipeline."""
import fire
from google.cloud import aiplatform as vertex_ai


def run_vertex_pipeline(
    template_path, display_name, project_id, region, enable_caching=False
):
    vertex_ai.init(project=project_id, location=region)

    pipeline = vertex_ai.PipelineJob(
        display_name=display_name,
        template_path=template_path,
        enable_caching=enable_caching,
    )

    pipeline.run()


if __name__ == "__main__":
    fire.Fire(run_vertex_pipeline)
