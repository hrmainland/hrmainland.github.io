#!/bin/bash
set -e

cd "$(dirname "$0")"

git pull

pip install -q -r requirements.txt

python report.py
