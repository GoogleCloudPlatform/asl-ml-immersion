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
#
all: clean install

kernels: \
 object_detection_kernel \
 pytorch_kfp_kernel \
 langchain_kernel \
 langchain_components_kernel \
 lit_kernel

.PHONY: clean
clean:
	@find . -name '*.pyc' -delete
	@find . -name '*.pytest_cache' -delete
	@find . -name '__pycache__' -delete
	@find . -name '*egg-info' -delete

.PHONY: install
install:
	@pip install --user -U pip
	@pip install --user "Cython<3"
	@pip install --user -e .
	@pip install --user --no-deps -r requirements-without-deps.txt
	@./scripts/setup_on_jupyterlab.sh
	@pre-commit install
	@sudo apt-get update
	@sudo apt-get -y install graphviz

.PHONY: precommit
precommit:
	@pre-commit run --all-files

.PHONY: asl_kernel
asl_kernel:
	./kernels/asl_kernel.sh

.PHONY: langchain_kernel
langchain_kernel:
	./kernels/langchain.sh

.PHONY: langchain_components_kernel
langchain_components_kernel:
	./kernels/langchain_components.sh

.PHONY: object_detection_kernel
object_detection_kernel:
	./kernels/object_detection.sh

.PHONY: pytorch_kfp_kernel
pytorch_kfp_kernel:
	./kernels/pytorch_kfp.sh

.PHONY: gemini_kernel
gemini_kernel:
	./kernels/gemini.sh

.PHONY: lit_kernel
lit_kernel:
	./kernels/lit.sh


.PHONY: tests
tests:
	pytest tests/unit
