"""Configure MLflow tracing for Claude Code sessions.

Merges MLflow env vars and a Stop hook into ~/.claude/settings.json so that
every Claude Code session automatically logs traces to a Databricks MLflow
experiment at /Users/{app_owner}/{app_name}.
"""

import os
import json
from pathlib import Path

# Set HOME if not properly set
if not os.environ.get("HOME") or os.environ["HOME"] == "/":
    os.environ["HOME"] = "/app/python/source_code"

home = Path(os.environ["HOME"])
settings_path = home / ".claude" / "settings.json"

# Read existing settings (written by setup_claude.py)
if settings_path.exists():
    settings = json.loads(settings_path.read_text())
else:
    settings = {}

app_owner = os.environ.get("APP_OWNER", "")
app_name = os.environ.get("DATABRICKS_APP_NAME", "coding-agents")

if not app_owner:
    print("MLflow tracing skipped: APP_OWNER not set")
    raise SystemExit(0)

experiment_name = f"/Users/{app_owner}/{app_name}"

tracing_enabled = os.environ.get("MLFLOW_CLAUDE_TRACING_ENABLED", "true").lower() != "false"

# Merge MLflow env vars
settings.setdefault("env", {})
settings["env"]["MLFLOW_CLAUDE_TRACING_ENABLED"] = str(tracing_enabled).lower()
settings["env"]["MLFLOW_TRACKING_URI"] = "databricks"
settings["env"]["MLFLOW_EXPERIMENT_NAME"] = experiment_name
# Override container-level OTEL endpoint so MLflow uses its native MlflowV3SpanExporter
# instead of sending traces to a non-existent localhost:4314 OTLP collector
settings["env"]["OTEL_EXPORTER_OTLP_ENDPOINT"] = ""

if tracing_enabled:
    # Pin --project to the app directory so mlflow resolves from the app's venv,
    # not from whatever project the user happens to be working in.
    app_dir = os.path.dirname(os.path.abspath(__file__))
    mlflow_hook = {
        "hooks": [
            {
                "type": "command",
                "command": (
                    f'uv run --project "{app_dir}" python -c '
                    '"from mlflow.claude_code.hooks import stop_hook_handler; stop_hook_handler()"'
                ),
            }
        ]
    }

    existing_hooks = settings.get("hooks", {})
    stop_hooks = existing_hooks.get("Stop", [])
    stop_hooks.append(mlflow_hook)
    existing_hooks["Stop"] = stop_hooks
    settings["hooks"] = existing_hooks
    print(f"MLflow tracing enabled: experiment={experiment_name}")
else:
    print(f"MLflow tracing disabled (set MLFLOW_CLAUDE_TRACING_ENABLED=true to enable)")

settings_path.write_text(json.dumps(settings, indent=2))
print(f"  Tracking URI: databricks")
print(f"  Settings updated: {settings_path}")
