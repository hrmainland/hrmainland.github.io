#!/bin/bash
set -e

cd "$(dirname "$0")/.."

git pull

pip install -q -r simple/requirements.txt

python simple/report.py
