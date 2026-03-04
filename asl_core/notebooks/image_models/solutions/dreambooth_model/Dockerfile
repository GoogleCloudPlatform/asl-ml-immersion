FROM us-docker.pkg.dev/vertex-ai/training/tf-gpu.2-12.py310:latest
RUN pip install keras_cv==0.5.1 --upgrade --quiet

COPY . /code

WORKDIR /code

ENTRYPOINT ["python3", "dreambooth_trainer.py"]
