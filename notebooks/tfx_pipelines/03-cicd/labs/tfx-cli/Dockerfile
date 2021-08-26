FROM gcr.io/deeplearning-platform-release/tf2-cpu.2-3
COPY requirements.txt .
RUN python3 -m pip install -U -r requirements.txt

ENTRYPOINT ["tfx"]
