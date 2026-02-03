# Web Terminal Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a deployable web terminal for Databricks Apps with Claude Code pre-configured.

**Architecture:** Flask backend spawns PTY shells per WebSocket connection; xterm.js frontend renders terminal in browser; setup script configures Claude Code for Databricks model serving.

**Tech Stack:** Flask, flask-socketio, gevent, ptyprocess, xterm.js, Socket.IO

---

## Task 1: Create Project Dependencies

**Files:**
- Create: `requirements.txt`

**Step 1: Create requirements.txt**

```
flask>=2.0
flask-socketio>=5.0
gevent>=21.0
gevent-websocket>=0.10
ptyprocess>=0.7
claude-agent-sdk
```

**Step 2: Commit**

```bash
git add requirements.txt
git commit -m "feat: add Python dependencies for web terminal"
```

---

## Task 2: Create Claude Configuration Script

**Files:**
- Create: `setup_claude.py`

**Step 1: Create setup_claude.py**

```python
import os
import json
from pathlib import Path

# Create ~/.claude directory
claude_dir = Path.home() / ".claude"
claude_dir.mkdir(exist_ok=True)

# 1. Write settings.json for Databricks model serving
settings = {
    "env": {
        "ANTHROPIC_MODEL": "databricks-claude-sonnet-4-5",
        "ANTHROPIC_BASE_URL": f"{os.environ['DATABRICKS_HOST']}/serving-endpoints/anthropic",
        "ANTHROPIC_AUTH_TOKEN": os.environ["DATABRICKS_TOKEN"],
        "ANTHROPIC_CUSTOM_HEADERS": "x-databricks-use-coding-agent-mode: true"
    }
}

settings_path = claude_dir / "settings.json"
settings_path.write_text(json.dumps(settings, indent=2))

# 2. Write ~/.claude.json to skip onboarding (v2.0.65+ fix)
claude_json = {
    "hasCompletedOnboarding": True
}

claude_json_path = Path.home() / ".claude.json"
claude_json_path.write_text(json.dumps(claude_json, indent=2))

print(f"Claude configured: {settings_path}")
print(f"Onboarding skipped: {claude_json_path}")
```

**Step 2: Test script runs without error (mock env vars)**

```bash
DATABRICKS_HOST=https://example.databricks.com DATABRICKS_TOKEN=test python setup_claude.py
```

Expected: Prints paths, creates files in home directory

**Step 3: Verify files created**

```bash
cat ~/.claude/settings.json
cat ~/.claude.json
```

Expected: JSON files with correct structure

**Step 4: Commit**

```bash
git add setup_claude.py
git commit -m "feat: add Claude Code configuration script for Databricks"
```

---

## Task 3: Create Frontend HTML

**Files:**
- Create: `static/index.html`

**Step 1: Create static directory**

```bash
mkdir -p static
```

**Step 2: Create static/index.html**

```html
<!DOCTYPE html>
<html>
<head>
  <title>Terminal</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@xterm/xterm@5.3.0/css/xterm.css">
  <style>
    body { margin: 0; background: #1e1e1e; }
    #terminal { height: 100vh; width: 100vw; }
  </style>
</head>
<body>
  <div id="terminal"></div>

  <script src="https://cdn.jsdelivr.net/npm/@xterm/xterm@5.3.0/lib/xterm.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/@xterm/addon-fit@0.8.0/lib/addon-fit.js"></script>
  <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
  <script>
    // Initialize terminal
    const term = new Terminal({
      cursorBlink: true,
      theme: { background: '#1e1e1e' }
    });
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));
    fitAddon.fit();

    // Connect to backend
    const socket = io();

    // User types → send to backend
    term.onData(data => socket.emit('input', data));

    // Backend output → render in terminal
    socket.on('output', data => term.write(data));

    // Handle resize
    window.addEventListener('resize', () => fitAddon.fit());

    // Welcome message
    socket.on('connect', () => {
      term.write('\x1b[32mConnected. Type "claude" to start coding.\x1b[0m\r\n\r\n');
    });
  </script>
</body>
</html>
```

**Step 3: Commit**

```bash
git add static/index.html
git commit -m "feat: add xterm.js frontend for web terminal"
```

---

## Task 4: Create Flask Backend

**Files:**
- Create: `app.py`

**Step 1: Create app.py**

```python
import os
import pty
import select
import subprocess
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit, request

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="gevent")

# Store PTY file descriptors per session
sessions = {}


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@socketio.on("connect")
def handle_connect():
    """Spawn a new PTY bash shell for this connection."""
    try:
        master_fd, slave_fd = pty.openpty()
        pid = subprocess.Popen(
            ["/bin/bash"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            preexec_fn=os.setsid
        ).pid
        sessions[request.sid] = {"master_fd": master_fd, "pid": pid}
        socketio.start_background_task(read_pty_output, request.sid, master_fd)
    except Exception as e:
        emit("output", f"\x1b[31mError spawning shell: {e}\x1b[0m\r\n")


@socketio.on("input")
def handle_input(data):
    """Forward user input to the PTY."""
    fd = sessions.get(request.sid, {}).get("master_fd")
    if fd:
        os.write(fd, data.encode())


@socketio.on("disconnect")
def handle_disconnect():
    """Clean up PTY on disconnect."""
    session = sessions.pop(request.sid, None)
    if session:
        os.close(session["master_fd"])


def read_pty_output(sid, fd):
    """Read PTY output and send to browser."""
    while sid in sessions:
        if select.select([fd], [], [], 0.1)[0]:
            try:
                output = os.read(fd, 1024).decode(errors="replace")
                socketio.emit("output", output, to=sid)
            except OSError:
                socketio.emit("output", "\r\n\x1b[31mShell disconnected.\x1b[0m\r\n", to=sid)
                break


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8000)
```

**Step 2: Commit**

```bash
git add app.py
git commit -m "feat: add Flask backend with WebSocket PTY handling"
```

---

## Task 5: Create Databricks App Configuration

**Files:**
- Create: `app.yaml`

**Step 1: Create app.yaml**

```yaml
command:
  - bash
  - -c
  - "python setup_claude.py && python app.py"
env:
  - name: DATABRICKS_HOST
    value: https://fevm-serverless-9cefok.cloud.databricks.com
  - name: DATABRICKS_TOKEN
    valueFrom: DATABRICKS_TOKEN
```

**Step 2: Commit**

```bash
git add app.yaml
git commit -m "feat: add Databricks App deployment configuration"
```

---

## Task 6: Local Testing

**Step 1: Install dependencies**

```bash
uv pip install -r requirements.txt
```

**Step 2: Run the app locally**

```bash
python app.py
```

Expected: Server starts on http://0.0.0.0:8000

**Step 3: Test in browser**

Open http://localhost:8000 in browser.

Expected:
- Dark terminal appears
- Green "Connected" message shows
- Can type commands (ls, pwd, etc.)
- Output renders correctly

**Step 4: Test terminal functionality**

In the web terminal, run:
```bash
echo "hello world"
ls -la
pwd
```

Expected: Commands execute and output displays

**Step 5: Stop the server**

Press Ctrl+C in terminal running app.py

---

## Task 7: Final Commit

**Step 1: Verify all files present**

```bash
ls -la
ls -la static/
```

Expected structure:
```
xterm-experiment/
├── app.py
├── app.yaml
├── requirements.txt
├── setup_claude.py
├── static/
│   └── index.html
└── docs/
    └── plans/
        └── 2026-02-02-web-terminal-design.md
```

**Step 2: Final commit if any uncommitted changes**

```bash
git status
```

If changes exist:
```bash
git add -A
git commit -m "chore: finalize web terminal implementation"
```

---

## Deployment (Manual - After Local Testing)

Once local testing passes, deploy to Databricks:

```bash
# 1. Create the app (if not exists)
databricks apps create xterm-terminal

# 2. Set up secrets (one-time)
databricks secrets create-scope xterm-terminal
databricks secrets put-secret xterm-terminal DATABRICKS_TOKEN

# 3. Deploy
databricks apps deploy xterm-terminal --source-code-path .
```

---

## Summary

| Task | Description | Files |
|------|-------------|-------|
| 1 | Dependencies | requirements.txt |
| 2 | Claude config | setup_claude.py |
| 3 | Frontend | static/index.html |
| 4 | Backend | app.py |
| 5 | App config | app.yaml |
| 6 | Local test | - |
| 7 | Final commit | - |
