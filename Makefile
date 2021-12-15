all: clean install 

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
