#!/bin/bash 

echo "Setup Lambda Layer"

mkdir -p layer/python
pip install -r layer/requirements.txt -t layer/python --upgrade




