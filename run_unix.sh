#!/bin/bash
set -e
cd "$(dirname "$0")"

python3 aws_credential_environment_script.py
