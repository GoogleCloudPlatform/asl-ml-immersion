FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3.10 \
        python3.10-dev \
        python3.10-distutils \
        curl \
        ca-certificates \
        && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10 && \
    ln -s /usr/bin/python3.10 /usr/bin/python && \
    ln -s /usr/local/bin/pip3.10 /usr/bin/pip && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV USERNAME=jupyter
ENV HOME_DIR=/home/$USERNAME
ENV PATH="$HOME_DIR/.local/bin:$PATH"

RUN useradd -ms /bin/bash $USERNAME
USER $USERNAME
WORKDIR $HOME_DIR

COPY --chown=jupyter:jupyter requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir jupyterlab && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT []
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''"]
