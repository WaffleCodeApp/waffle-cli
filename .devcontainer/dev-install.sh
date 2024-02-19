#!/bin/bash

python -m venv .venv
source .venv/bin/activate
pip3 install -r .devcontainer/dev-requirements.txt
poetry completions bash >> ~/.bash_completion
