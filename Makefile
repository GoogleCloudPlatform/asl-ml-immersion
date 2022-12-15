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
kernels: reinforcement_learning_kernel


.PHONY: clean
clean:
	@find . -name '*.pyc' -delete
	@find . -name '*.pytest_cache' -delete
	@find . -name '__pycache__' -delete
	@find . -name '*egg-info' -delete

.PHONY: install
install:
	@pip install -U pip
	@pip install -r requirements.txt
	@pre-commit install

.PHONY: precommit
precommit:
	@pre-commit run --all-files


.PHONY: reinforcement_learning_kernel
reinforcement_learning_kernel:
	./kernels/reinforcement_learning.sh

.PHONY: tf_recommenders_kernel
tf_recommenders_kernel:
	./kernels/tf_recommenders.sh
