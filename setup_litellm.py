#!/usr/bin/env python
"""Start LiteLLM as a local proxy to sanitize empty content blocks before they reach Databricks.

OpenCode occasionally produces empty text content blocks in messages, which the Databricks
Foundation Model API rejects with: "messages: text content blocks must be non-empty"
(see https://github.com/sst/opencode/issues/5028).

LiteLLM strips these empty blocks before forwarding requests to the Databricks AI Gateway,
fixing the issue without forking OpenCode. The proxy runs on localhost:4000 (internal only,
never exposed externally).

Related: https://github.com/BerriAI/litellm/pull/20384
"""
import os
import sys
import json
import time
import subprocess
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

from utils import ensure_https

LITELLM_PORT = 4000
LITELLM_HOST = "127.0.0.1"
HEALTH_TIMEOUT = 30  # seconds to wait for LiteLLM to be ready
HEALTH_POLL_INTERVAL = 1  # seconds between health checks

# Set HOME if not properly set
if not os.environ.get("HOME") or os.environ["HOME"] == "/":
    os.environ["HOME"] = "/app/python/source_code"

home = Path(os.environ["HOME"])

# Databricks configuration
gateway_host = ensure_https(os.environ.get("DATABRICKS_GATEWAY_HOST", "").rstrip("/"))
host = ensure_https(os.environ.get("DATABRICKS_HOST", "").rstrip("/"))
token = os.environ.get("DATABRICKS_TOKEN", "")

if not token:
    print("Warning: DATABRICKS_TOKEN not set, skipping LiteLLM proxy setup")
    sys.exit(0)

# Determine the upstream base URL (AI Gateway or direct serving endpoints)
if gateway_host:
    upstream_base = f"{gateway_host}/mlflow/v1"
    print(f"LiteLLM proxy will forward to AI Gateway: {gateway_host}")
else:
    upstream_base = f"{host}/serving-endpoints"
    print(f"LiteLLM proxy will forward to: {host}/serving-endpoints")

# Build LiteLLM config
# Models use the databricks/ prefix so LiteLLM's sanitization logic activates
# (see https://github.com/BerriAI/litellm/pull/20384)
litellm_config = {
    "model_list": [
        {
            "model_name": "databricks-claude-opus-4-6",
            "litellm_params": {
                "model": "databricks/databricks-claude-opus-4-6",
                "api_key": f"os.environ/DATABRICKS_TOKEN",
                "api_base": upstream_base,
            }
        },
        {
            "model_name": "databricks-claude-sonnet-4-6",
            "litellm_params": {
                "model": "databricks/databricks-claude-sonnet-4-6",
                "api_key": f"os.environ/DATABRICKS_TOKEN",
                "api_base": upstream_base,
            }
        },
        {
            "model_name": "databricks-gemini-2-5-flash",
            "litellm_params": {
                "model": "databricks/databricks-gemini-2-5-flash",
                "api_key": f"os.environ/DATABRICKS_TOKEN",
                "api_base": upstream_base,
            }
        },
        {
            "model_name": "databricks-gemini-2-5-pro",
            "litellm_params": {
                "model": "databricks/databricks-gemini-2-5-pro",
                "api_key": f"os.environ/DATABRICKS_TOKEN",
                "api_base": upstream_base,
            }
        },
        {
            "model_name": "databricks-gemini-3-1-pro",
            "litellm_params": {
                "model": "databricks/databricks-gemini-3-1-pro",
                "api_key": f"os.environ/DATABRICKS_TOKEN",
                "api_base": upstream_base,
            }
        },
    ],
    "litellm_settings": {
        "drop_params": True,  # Drop unsupported params instead of erroring
    },
    "general_settings": {
        "master_key": None,  # No auth needed for localhost-only proxy
    }
}

# Write config
config_dir = home / ".config" / "litellm"
config_dir.mkdir(parents=True, exist_ok=True)
config_path = config_dir / "config.yaml"

# LiteLLM accepts YAML; write as JSON which is valid YAML
config_path.write_text(json.dumps(litellm_config, indent=2))

print(f"LiteLLM config written to {config_path}")

# Start LiteLLM as a background process
log_path = home / ".litellm-proxy.log"
print(f"Starting LiteLLM proxy on {LITELLM_HOST}:{LITELLM_PORT}...")

proc = subprocess.Popen(
    [
        sys.executable, "-m", "litellm",
        "--config", str(config_path),
        "--host", LITELLM_HOST,
        "--port", str(LITELLM_PORT),
    ],
    stdout=open(log_path, "w"),
    stderr=subprocess.STDOUT,
    env=os.environ.copy(),
    start_new_session=True,  # Detach from parent process group
)

# Write PID file for cleanup
pid_path = home / ".litellm-proxy.pid"
pid_path.write_text(str(proc.pid))
print(f"LiteLLM proxy started (PID: {proc.pid})")

# Wait for health check
health_url = f"http://{LITELLM_HOST}:{LITELLM_PORT}/health"
start = time.time()
ready = False

while time.time() - start < HEALTH_TIMEOUT:
    try:
        resp = urlopen(Request(health_url), timeout=2)
        if resp.status == 200:
            ready = True
            break
    except (URLError, OSError):
        pass

    # Check if process died
    if proc.poll() is not None:
        print(f"Error: LiteLLM proxy exited with code {proc.returncode}")
        print(f"Check logs at {log_path}")
        sys.exit(1)

    time.sleep(HEALTH_POLL_INTERVAL)

if ready:
    elapsed = time.time() - start
    print(f"LiteLLM proxy ready on {LITELLM_HOST}:{LITELLM_PORT} ({elapsed:.1f}s)")
else:
    print(f"Warning: LiteLLM health check timed out after {HEALTH_TIMEOUT}s")
    print(f"Proxy may still be starting — check logs at {log_path}")
