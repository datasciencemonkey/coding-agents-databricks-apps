#!/usr/bin/env python
"""Configure Hermes Agent with Databricks Model Serving.

Hermes Agent (github.com/NousResearch/hermes-agent) is a multi-provider AI CLI
with tool-calling, persistent memory, slash commands, and a rich skill system.

Unlike the other CLIs in CoDA, Hermes is a Python application (not npm).
This script performs a LEAN install (bypassing the upstream installer's
`.[all]` extras, which pull ~500 MB / 90+ packages) by cloning the repo
and installing only the extras CoDA actually needs:

    [mcp, messaging, matrix, web, acp]    # ~180 MB, ~90 s on Databricks Apps

This covers Hermes's three CoDA-required capabilities:
  1. Self-improvement via MCP (deepwiki, exa)
  2. Pre-wired Databricks Model Serving (core dep — no extra needed)
  3. Open path for messaging (WhatsApp / Slack / Teams / Matrix / Discord)

Users can add more later via `uv pip install -e ".[voice,rl,feishu,...]"`
inside ~/.hermes/hermes-agent, or via `hermes setup` / `hermes mcp add`.

Config: ~/.hermes/config.yaml with custom provider for Databricks.
Auth:   Bearer token via Databricks PAT.

Config precedence (matches Claude/Codex/Gemini/OpenCode setup):
  1. If DATABRICKS_GATEWAY_HOST or DATABRICKS_WORKSPACE_ID -> AI Gateway
  2. Otherwise -> DATABRICKS_HOST/serving-endpoints

Opt-out:
  Set ENABLE_HERMES=false in app.yaml to skip installation entirely.
"""
import os
import subprocess
from pathlib import Path

from utils import adapt_instructions_file, ensure_https, get_gateway_host

# Opt-out: allow operators to disable Hermes bundling without removing the file.
if os.environ.get("ENABLE_HERMES", "true").strip().lower() in ("false", "0", "no"):
    print("ENABLE_HERMES=false — skipping Hermes Agent setup")
    raise SystemExit(0)

# Set HOME if not properly set
if not os.environ.get("HOME") or os.environ["HOME"] == "/":
    os.environ["HOME"] = "/app/python/source_code"

home = Path(os.environ["HOME"])

host = os.environ.get("DATABRICKS_HOST", "")
token = os.environ.get("DATABRICKS_TOKEN", "")
hermes_model = os.environ.get("HERMES_MODEL", "databricks-claude-opus-4-7")
hermes_fallback_model = os.environ.get("HERMES_FALLBACK_MODEL", "databricks-claude-opus-4-6")

hermes_home = home / ".hermes"
hermes_install_dir = hermes_home / "hermes-agent"
hermes_venv = hermes_install_dir / "venv"
hermes_venv_bin = hermes_venv / "bin" / "hermes"
hermes_bin = home / ".local" / "bin" / "hermes"

# Lean extras — covers MCP (self-improvement), messaging paths (WhatsApp/Slack/
# Teams via matrix bridges), and ACP (agent-to-agent protocol). Excludes voice,
# rl, feishu, dingtalk, bedrock, mistral, modal, daytona — users opt in later.
HERMES_EXTRAS = "mcp,messaging,matrix,web,acp"
HERMES_REPO = "https://github.com/NousResearch/hermes-agent.git"

# 1. Install Hermes Agent (always, even without token).
local_bin = home / ".local" / "bin"
local_bin.mkdir(parents=True, exist_ok=True)
hermes_home.mkdir(parents=True, exist_ok=True)


def _run(cmd, **kwargs):
    """Run a subprocess command and return (rc, stdout, stderr)."""
    result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
    return result.returncode, result.stdout, result.stderr


if not hermes_bin.exists() or not hermes_venv_bin.exists():
    print(f"Installing Hermes Agent (lean extras: [{HERMES_EXTRAS}])...")

    # 1a. Clone (or update) the repo.
    if not hermes_install_dir.exists():
        rc, _, err = _run(
            ["git", "clone", "--depth", "1", HERMES_REPO, str(hermes_install_dir)],
            timeout=180,
        )
        if rc != 0:
            print(f"Hermes git clone failed (rc={rc}): {err[-600:]}")
            raise SystemExit(0)  # soft-fail — don't crash app startup
    else:
        # Best-effort pull; ignore failures (detached HEAD, local edits, etc.)
        _run(["git", "-C", str(hermes_install_dir), "pull", "--ff-only"], timeout=60)

    # 1b. Create venv with uv.
    if not hermes_venv.exists():
        rc, _, err = _run(
            ["uv", "venv", str(hermes_venv)],
            timeout=120,
        )
        if rc != 0:
            print(f"Hermes venv create failed (rc={rc}): {err[-600:]}")
            raise SystemExit(0)

    # 1c. Install with lean extras using uv (fast + respects pyproject extras).
    install_env = {
        **os.environ,
        "VIRTUAL_ENV": str(hermes_venv),
        "PATH": f"{hermes_venv / 'bin'}:{os.environ.get('PATH', '')}",
    }
    rc, _, err = _run(
        ["uv", "pip", "install", "-e", f".[{HERMES_EXTRAS}]"],
        cwd=str(hermes_install_dir),
        env=install_env,
        timeout=600,
    )
    if rc != 0:
        # Fall back to bare install so `hermes` at least launches.
        print(f"Hermes lean install failed (rc={rc}), falling back to base: {err[-400:]}")
        rc, _, err = _run(
            ["uv", "pip", "install", "-e", "."],
            cwd=str(hermes_install_dir),
            env=install_env,
            timeout=600,
        )
        if rc != 0:
            print(f"Hermes base install also failed (rc={rc}): {err[-600:]}")
            raise SystemExit(0)

    # 1d. Symlink launcher into ~/.local/bin/hermes.
    if hermes_venv_bin.exists():
        if hermes_bin.exists() or hermes_bin.is_symlink():
            hermes_bin.unlink()
        hermes_bin.symlink_to(hermes_venv_bin)
        print(f"Hermes Agent installed -> {hermes_bin} -> {hermes_venv_bin}")
    else:
        print(f"Warning: expected venv binary missing: {hermes_venv_bin}")
else:
    print(f"Hermes Agent already installed at {hermes_bin}")

# 1e. Pre-create standard Hermes runtime dirs so first run doesn't race on mkdir.
for sub in ("sessions", "logs", "memories", "skills", "cron", "pairing",
            "hooks", "image_cache", "audio_cache"):
    (hermes_home / sub).mkdir(parents=True, exist_ok=True)

# 2. Skip auth config if no token (will be configured after PAT setup)
if not host or not token:
    print("Hermes Agent installed — config will be set after PAT setup")
    raise SystemExit(0)

# Strip trailing slash and ensure https:// prefix
host = ensure_https(host.rstrip("/"))

gateway_host = get_gateway_host()
gateway_token = os.environ.get("DATABRICKS_TOKEN", "") if gateway_host else ""
if gateway_host and not gateway_token:
    print("Warning: AI Gateway resolved but DATABRICKS_TOKEN missing, falling back to DATABRICKS_HOST")
    gateway_host = ""

if gateway_host:
    base_url = f"{gateway_host}/mlflow/v1"
    auth_token = gateway_token
    print(f"Using Databricks AI Gateway: {gateway_host}")
else:
    base_url = f"{host}/serving-endpoints"
    auth_token = token
    print(f"Using Databricks Host: {host}")

# 3. Write ~/.hermes/config.yaml
config_path = hermes_home / "config.yaml"

claude_skills_dir = Path("/app/python/source_code/.claude/skills")
external_skills = [str(claude_skills_dir)] if claude_skills_dir.exists() else []

model_catalog = [
    "databricks-claude-opus-4-6",
    "databricks-claude-sonnet-4-6",
    "databricks-claude-haiku-4-5",
    "databricks-gpt-5-3-codex",
    "databricks-gpt-5-1-codex-max",
    "databricks-gemini-2-5-flash",
    "databricks-gemini-2-5-pro",
    "databricks-gemini-3-1-pro",
]

lines = []
lines.append("# Hermes Agent config — generated by setup_hermes.py")
lines.append("# Regenerate by re-running: uv run python setup_hermes.py")
lines.append("")
lines.append("model:")
lines.append(f"  default: {hermes_model}")
lines.append("  provider: custom")
lines.append(f"  base_url: {base_url}")
lines.append(f"  api_key: {auth_token}")
lines.append("")
lines.append("# Fallback chain — triggers on 429 (rate limit), 529 (overload),")
lines.append("# 503 (service errors), or connection failures.")
lines.append("fallback_providers:")
lines.append("- provider: custom")
lines.append(f"  model: {hermes_fallback_model}")
lines.append(f"  base_url: {base_url}")
lines.append(f"  api_key: {auth_token}")
lines.append("")
lines.append("# External skills — Claude Code skill directory (shared with other agents)")
lines.append("skills:")
if external_skills:
    lines.append("  external_dirs:")
    for d in external_skills:
        lines.append(f"    - {d}")
else:
    lines.append("  external_dirs: []")
lines.append("")
lines.append("# Native MCP servers — DeepWiki (GitHub wiki lookup) + Exa (web search)")
lines.append("mcp_servers:")
lines.append("  deepwiki:")
lines.append("    url: https://mcp.deepwiki.com/mcp")
lines.append("    timeout: 60")
lines.append("  exa:")
lines.append("    url: https://mcp.exa.ai/mcp")
lines.append("    timeout: 60")

team_memory_url = os.environ.get("TEAM_MEMORY_MCP_URL", "").strip().rstrip("/")
if team_memory_url:
    lines.append("  team-memory:")
    lines.append(f"    url: {team_memory_url}/mcp")
    lines.append("    timeout: 60")
    print(f"Team memory MCP configured: {team_memory_url}/mcp")

lines.append("")
lines.append("# Model catalog hint — users can `/model` switch inside chat")
lines.append("display:")
lines.append("  known_models:")
for m in model_catalog:
    lines.append(f"    - {m}")
lines.append("")

should_write = True
if config_path.exists():
    existing = config_path.read_text()
    if "generated by setup_hermes.py" not in existing and "provider: custom" in existing:
        print(f"Existing {config_path} looks hand-edited — preserving it (skipping rewrite)")
        should_write = False

if should_write:
    config_path.write_text("\n".join(lines))
    print(f"Hermes config written: {config_path}")

# 4. Adapt CLAUDE.md -> ~/.hermes/HERMES.md for first-run context
claude_md_locations = [
    Path(__file__).parent / "CLAUDE.md",
    home / ".claude" / "CLAUDE.md",
    Path("/app/python/source_code/CLAUDE.md"),
]

claude_md_path = None
for loc in claude_md_locations:
    if loc.exists():
        claude_md_path = loc
        break

hermes_md = hermes_home / "HERMES.md"
adapt_instructions_file(
    source_path=claude_md_path or claude_md_locations[0],
    target_path=hermes_md,
    new_header="# Hermes Agent on Databricks",
    cli_name="Hermes",
)

# 5. Create projects directory (parity with other agents)
projects_dir = home / "projects"
projects_dir.mkdir(exist_ok=True)

print("\nHermes Agent ready! Usage:")
print("  hermes chat                    # Interactive chat")
print("  hermes --tui chat              # Rich Ink TUI")
print("  hermes model                   # Select default model")
print("  hermes setup                   # Reconfigure wizard")
print("  hermes mcp add <name> <url>    # Add MCP server")
print(f"\nEndpoint:       {base_url}")
print(f"Primary model:  {hermes_model}")
print(f"Fallback model: {hermes_fallback_model} (auto-activates on 429/529/503)")
print(f"Extras:         [{HERMES_EXTRAS}]  (add more: uv pip install -e \".[voice,...]\")")
print("Auth:           Bearer token (Databricks PAT)")
