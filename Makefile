# Copyright 2025 Google LLC. All Rights Reserved.
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

SHELL := /bin/bash
export PATH := $(HOME)/.local/bin:$(PATH)
SETUP_SCRIPT = ./scripts/setup_kernel.sh

PROJECTS = \
	asl_core:asl_core:"ASL Core" \
	asl_agent:asl_agent:"ASL Agent" \
	asl_mlops:asl_mlops:"ASL MLOps"

.PHONY: all install clean setup dev build-kernels

all: setup build-kernels

install: setup build-kernels

dev: install install-pre-commit

clean:
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete
	@find . -type d -name '*.egg-info' -exec rm -rf {} +

	@for config in $(PROJECTS); do \
		IFS=: read -r dir name disp <<< "$$config"; \
		bash $(SETUP_SCRIPT) $$dir $$name "$$disp" remove; \
	done

setup:
	./scripts/setup_on_jupyterlab.sh
	sudo apt-get update && sudo apt-get -y install graphviz
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	uv python install 3.10
	uv tool install jupyter-core --with jupyter-client

build-kernels:
	@for config in $(PROJECTS); do \
		IFS=: read -r dir name disp <<< "$$config"; \
		bash $(SETUP_SCRIPT) $$dir $$name "$$disp"; \
	done

install-pre-commit:
	uv tool install pre-commit
	pre-commit install
