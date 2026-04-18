#!/usr/bin/env bash
# Stop hook: flush the Claude Code session transcript to an MLflow trace.
#
# Runs async with a hard timeout so a stall in transcript processing
# (the known-issue the setup_mlflow.py top comment calls out) cannot:
#   - block the Stop-hook chain (crystallize-nudge, brain-push, /til)
#   - hold a background process open consuming memory/CPU indefinitely
#
# 30s is generous — a normal flush is sub-second. If it runs past that,
# we drop this one trace and move on.

set -euo pipefail

APP_DIR="/app/python/source_code"
LOG="$HOME/.mlflow-hook.log"

nohup timeout 30 \
  uv run --project "$APP_DIR" python -c \
    "from mlflow.claude_code.hooks import stop_hook_handler; stop_hook_handler()" \
  >> "$LOG" 2>&1 & disown
