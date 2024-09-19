# Use the latest Ubuntu image as the base image
FROM ubuntu:latest

# Set the working directory inside the container
WORKDIR /app

COPY . .

# Update the package list to ensure we have the latest information on available packages
RUN apt-get update -y

# Install git for version control
# RUN apt-get install -y python3 git
RUN apt-get install -y python3 python3-venv git

# Clone the pyenv repository to manage Python versions
RUN git clone https://github.com/pyenv/pyenv.git /app/.pyenv

# Set environment variables for pyenv
ENV PYENV_ROOT="/app/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PATH"

# Install necessary build dependencies for Python compilation
RUN apt-get -y install build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Install a specific version of Python (3.9.2) using pyenv
RUN pyenv install 3.9.2

# Set the global Python version to 3.9.2
RUN pyenv global 3.9.2

# RUN eval "$(pyenv init -)" && pip install virtualenv
RUN eval "$(pyenv init -)" && ./scripts/linux/install.sh local

# RUN python3 -m venv .venv/

# ENTRYPOINT [".venv/bin/python", "main.py", "--local"]
CMD [".venv/bin/python", "main.py", "--local"]
