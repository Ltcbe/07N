#!/bin/bash
set -e

python /app/app/prestart.py
uvicorn app.main:app --host 0.0.0.0 --port 1788
