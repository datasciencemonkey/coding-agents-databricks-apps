# Web Terminal for Databricks Apps with Claude Code

**Date:** 2026-02-02
**Status:** Approved

## Overview

A web-based terminal emulator deployed as a Databricks App that provides shell access to the container, with Claude Code pre-configured for vibe coding.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Databricks App Container                  │
│                                                              │
│  ┌──────────────┐      WebSocket       ┌──────────────────┐ │
│  │              │◄────────────────────►│                  │ │
│  │  Flask App   │                      │   PTY Process    │ │
│  │  (Backend)   │                      │   (bash shell)   │ │
│  │              │                      │                  │ │
│  └──────┬───────┘                      │  ┌────────────┐  │ │
│         │                              │  │Claude Code │  │ │
│         │ serves                       │  │  (CLI)     │  │ │
│         ▼                              │  └────────────┘  │ │
│  ┌──────────────┐                      └──────────────────┘ │
│  │  xterm.js    │                                           │
│  │  (Frontend)  │                                           │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
         ▲
         │ HTTPS
         ▼
┌─────────────────┐
│  User Browser   │
└─────────────────┘
```

## Components

### Backend (Flask + WebSocket + PTY)

- **Flask** serves the static frontend
- **flask-socketio** handles WebSocket connections
- **ptyprocess** spawns bash shells
- Each connection gets its own PTY session

### Frontend (xterm.js)

- Terminal emulator in the browser
- Loaded from CDN
- Socket.IO client for WebSocket communication
- Auto-resizes to viewport

### Claude Code Configuration

Uses Databricks model serving instead of direct Anthropic API:

| File | Purpose |
|------|---------|
| `~/.claude/settings.json` | Databricks model serving config |
| `~/.claude.json` | Skip onboarding prompt (v2.0.65+ fix) |

## Project Structure

```
xterm-experiment/
├── app.py                 # Flask + WebSocket + PTY
├── setup_claude.py        # Pre-configures Claude for Databricks
├── requirements.txt
├── app.yaml
└── static/
    └── index.html
```

## Files

### requirements.txt

```
flask>=2.0
flask-socketio>=5.0
gevent>=21.0
gevent-websocket>=0.10
ptyprocess>=0.7
claude-agent-sdk
```

### app.yaml

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

### app.py

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

### setup_claude.py

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

### static/index.html

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

## Deployment

1. **Create the app:**
   ```bash
   databricks apps create xterm-terminal
   ```

2. **Set the token secret:**
   ```bash
   databricks secrets create-scope xterm-terminal
   databricks secrets put-secret xterm-terminal DATABRICKS_TOKEN
   ```

3. **Deploy:**
   ```bash
   databricks apps deploy xterm-terminal --source-code-path .
   ```

## Known Limitations

| Limitation | Impact | Workaround |
|------------|--------|------------|
| No persistence | Files lost on redeploy | Mount workspace volume (future) |
| Single user per session | Each tab = new shell | Expected behavior |
| 12hr Databricks session limit | Long sessions timeout | User reconnects |
| No terminal resize signaling | Fixed size initially | Can add SIGWINCH handling |
| Container resources | Limited CPU/memory | Use for coding, not heavy compute |

## Security Considerations

- Shell runs as app user (not root)
- Databricks token scoped to model serving
- No network egress restrictions by default (Claude can `curl`, `git clone`, etc.)

## Future Enhancements

- Persistent workspace via mounted volumes
- Multi-user authentication
- Terminal resize signaling (SIGWINCH)
- Session recording/playback
