FROM us-docker.pkg.dev/vertex-ai/training/sklearn-cpu.1-0
RUN pip install -U fire cloudml-hypertune scikit-learn==1.2.2
WORKDIR /app
COPY train.py .

ENTRYPOINT ["python", "train.py"]
