#!/usr/bin/env bash
set -euo pipefail
source .venv/bin/activate || python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python volatility_tracker.py --top 25 --min-mcap 100000000 --min-vol 10000000
