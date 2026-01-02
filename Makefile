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
ENVS = asl_core asl_agent asl_mlops

.PHONY: clean setup dev $(ENVS)

all: setup $(ENVS)

install: setup $(ENVS)

install-dev: install dev

clean:
	@find . -name '*.pyc' -delete
	@find . -name '*.pytest_cache' -delete
	@find . -name '__pycache__' -delete

	@echo "Removing Kernels and Venvs..."
	@for env in $(ENVS); do \
		bash $$env/setup_env.sh remove; \
    	rm -rf ./$$env/asl.egg-info; \
	done

setup:
	./scripts/setup_on_jupyterlab.sh
	sudo apt-get update
	sudo apt-get -y install graphviz
	curl -LsSf https://astral.sh/uv/install.sh | sh;
	. $(HOME)/.local/bin/env

dev:
	pip install -U pre-commit pytest
	pre-commit install

<<<<<<< HEAD
.PHONY: pytorch_kfp_kernel
pytorch_kfp_kernel:
	./kernels/pytorch_kfp.sh

.PHONY: tf_privacy_kernel
tf_privacy_kernel:
	./kernels/tf_privacy.sh

.PHONY: keras_cv_kernel
keras_cv_kernel:
	./kernels/keras_cv.sh

.PHONY: tests
tests:
	pytest tests/unit
=======
$(ENVS):
	@echo "=== Building Environment for $@ ==="
	@bash $@/setup_env.sh
>>>>>>> 7fd72def (WIP: testing modular approach)
