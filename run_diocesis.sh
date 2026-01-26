#!/bin/zsh
set -euo pipefail

export DIOCESIS_USERNAME="$(security find-generic-password -a "$USER" -s "diocesis.username" -w)"
export DIOCESIS_PASSWORD="$(security find-generic-password -a "$USER" -s "diocesis.password" -w)"

"/Users/gabops/Downloads/Diocesis/.venv/bin/python" "/Users/gabops/Downloads/Diocesis/import os.py"
