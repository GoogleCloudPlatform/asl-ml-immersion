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
PYTHON_VERSION = 3.12

PROJECTS = \
	asl_core:asl_core:"ASL Core" \
	asl_genai:asl_genai:"ASL Gen AI" \
	asl_mlops:asl_mlops:"ASL MLOps"

.PHONY: all install clean setup-apt setup-ide setup build-kernels tf_privacy_kernel keras_cv_kernel

all: setup build-kernels install-pre-commit

install: all

clean:
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete
	@find . -type d -name '*.egg-info' -exec rm -rf {} +

	@for config in $(PROJECTS); do \
		IFS=: read -r dir name disp <<< "$$config"; \
		bash $(SETUP_SCRIPT) $$dir $$name "$$disp" remove; \
	done

setup-apt:
	$(eval TOKEN=$(shell curl -s -H "Metadata-Flavor: Google" http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token | sed 's/.*"access_token":"\([^"]*\)".*/\1/'))
	@export CLOUDSDK_AUTH_ACCESS_TOKEN=$(TOKEN); \
	export GOOGLE_APPLICATION_CREDENTIALS=""; \
	sudo rm -f /etc/apt/sources.list.d/yarn.list /usr/share/keyrings/yarn.gpg; \
	curl -fsSL https://dl.yarnpkg.com/debian/pubkey.gpg | sudo gpg --dearmor -o /usr/share/keyrings/yarn.gpg; \
	echo "deb [signed-by=/usr/share/keyrings/yarn.gpg] https://dl.yarnpkg.com/debian/ stable main" | sudo tee /etc/apt/sources.list.d/yarn.list; \
	sudo apt-get update

setup-ide:
	@if command -v code-oss-cloud-workstations > /dev/null; then \
		echo "Installing Workstation extensions..."; \
		code-oss-cloud-workstations --install-extension ms-python.python --force; \
		code-oss-cloud-workstations --install-extension ms-toolsai.jupyter --force; \
	fi

setup: setup-apt setup-ide
	sudo apt-get -y install graphviz
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
	uv python install $(PYTHON_VERSION)
	uv tool install jupyter-core --with jupyter-client
	@grep -q "local/bin" ~/.bashrc || echo 'export PATH="$$HOME/.local/bin:$$PATH"' >> ~/.bashrc

# Build main kernels
build-kernels:
	@for config in $(PROJECTS); do \
		IFS=: read -r dir name disp <<< "$$config"; \
		bash $(SETUP_SCRIPT) $$dir $$name "$$disp"; \
	done

# Build Special Kernels
tf_privacy_kernel:
	./asl_core/kernels/tf_privacy.sh

keras_cv_kernel:
	./asl_core/kernels/keras_cv.sh

install-pre-commit:
	uv tool install pre-commit
	uv tool run pre-commit install
