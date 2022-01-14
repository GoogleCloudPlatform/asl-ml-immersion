# Use the official Python image.
# https://hub.docker.com/_/python
FROM python:3.8

# Install python client.
RUN pip install google-api-python-client
RUN pip install --upgrade google-cloud-aiplatform

# Copy local code to the container image.
COPY ./vertex_upload_model.py ./

# Set entrypoint.
ENTRYPOINT ["python3", "./vertex_upload_model.py"]