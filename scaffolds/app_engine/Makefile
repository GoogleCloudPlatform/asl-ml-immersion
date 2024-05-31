all: clean venv

.PHONY: clean
clean:
	@find . -name '*.pyc' -delete
	@find . -name '__pycache__' -delete
	@find . -name '*egg-info' -type d -exec rm -r {} +
	@find . -name  '.pytest_cache' -type d -exec rm -r {} +
	@rm -rf venv

.PHONY: venv
venv:
	@python3 -m venv venv
	@. venv/bin/activate && pip install -U pip && pip install  -e .

.PHONY: auth
auth:
	gcloud auth application-default login

.PHONY: tests
tests:
	./scripts/run_tests.sh

.PHONY: ingest
ingest: 
	./scripts/upload_data_to_gcs.sh
	./scripts/generate_embeddings.sh


.PHONY: deploy
deploy: clean
	./scripts/create_app.sh
	./scripts/deploy.sh

.PHONY: run
run:
	./scripts/run_locally.sh

.PHONY: notebook
notebook:
	@. venv/bin/activate && jupyter lab
