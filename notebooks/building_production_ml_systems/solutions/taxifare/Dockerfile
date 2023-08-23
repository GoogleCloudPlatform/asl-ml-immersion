FROM us-docker.pkg.dev/vertex-ai/training/tf-cpu.2-12.py310:latest
# TODO 3

COPY . /code

WORKDIR /code

ENTRYPOINT ["python3", "-m", "trainer.task"]
