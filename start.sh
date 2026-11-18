#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"

export PYTHONPATH="$PWD/.deps${PYTHONPATH:+:$PYTHONPATH}"
if [[ ! -f .deps/.installed ]] || [[ requirements.txt -nt .deps/.installed ]]; then
    python3 -m pip install --upgrade --target .deps -r requirements.txt
    touch .deps/.installed
fi

exec python3 app.py
