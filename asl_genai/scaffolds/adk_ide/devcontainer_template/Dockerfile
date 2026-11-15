FROM python:3.13-slim

# Define the user name and IDs
ARG USERNAME=dev_adk
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Install git and sudo
RUN apt-get update && apt-get install -y \
    git \
    sudo \
    && rm -rf /var/lib/apt/lists/*

# Create the user and group, give them a home directory, and set bash as the default shell
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m -s /bin/bash $USERNAME \
    # Add sudo support for the non-root user
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Copy uv and uvx directly from Astral's official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Optimize uv behavior in containerized environments
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

# (Optional) Switch to the user within the Dockerfile itself
# USER $USERNAME