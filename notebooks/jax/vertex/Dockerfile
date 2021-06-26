FROM gcr.io/deeplearning-platform-release/tf2-gpu.2-5

COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt -f https://storage.googleapis.com/jax-releases/jax_releases.html
