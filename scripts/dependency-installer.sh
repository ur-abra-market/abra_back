#!/bin/bash

# Update the list of available packages
sudo apt update

# Install the necessary packages for development and Python environment
sudo apt -y install make docker build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

# Download and install pyenv (a tool for managing multiple Python versions)
curl -sS https://pyenv.run | bash

# Add pyenv settings to .bashrc for automatic initialization of pyenv on shell startup
echo '
# pyenv
export PATH="$HOME/.pyenv/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
' >> ~/.bashrc

# Install Python version 3.11.1 using pyenv and set it as the local version for the current directory
sudo pyenv install 3.11.1 && pyenv local 3.11.1
# Upgrade pip and install Poetry (a dependency management and packaging tool)
pip install -U pip && pip install poetry
# Configure Poetry to create virtual environments inside the project directory
poetry config virtualenvs.in-project true
# Install project dependencies specified in pyproject.toml
poetry install
