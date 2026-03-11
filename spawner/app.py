"""Coding Agents Spawner App -- one-click provisioning of coding-agents for any developer."""

import os
import uuid

import requests
from flask import Flask, jsonify, request

app = Flask(__name__, static_folder="static")

_raw_host = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_HOST = (
    _raw_host if _raw_host.startswith("https://") else f"https://{_raw_host}"
).rstrip("/")

# Admin token for provisioning operations (secret scope, app creation, etc.)
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")


def app_name_from_email(email: str) -> str:
    """Derive app name from user email: david.okeeffe@company.com -> coding-agents-david-okeeffe."""
    username = email.split("@")[0]
    slug = username.replace(".", "-").replace("_", "-").lower()
    return f"coding-agents-{slug}"


def resolve_pat_owner(host: str, pat: str) -> str:
    """Call /api/2.0/preview/scim/v2/Me to get the email of the PAT owner."""
    resp = requests.get(
        f"{host}/api/2.0/preview/scim/v2/Me",
        headers={"Authorization": f"Bearer {pat}"},
    )
    resp.raise_for_status()
    data = resp.json()
    return data.get("userName", "")


def store_pat_in_secret_scope(
    host: str, oauth_token: str, app_name: str, pat_value: str, secret_key: str
) -> dict:
    """Create secret scope (handle 409) and store PAT with unique key."""
    scope_name = f"{app_name}-secrets"
    headers = {"Authorization": f"Bearer {oauth_token}"}

    # Create scope -- 409 means it already exists, which is fine
    scope_resp = requests.post(
        f"{host}/api/2.0/secrets/scopes/create",
        headers=headers,
        json={"scope": scope_name},
    )
    if scope_resp.status_code not in (200, 409) and "ALREADY_EXISTS" not in scope_resp.text:
        raise RuntimeError(f"Failed to create secret scope: {scope_resp.status_code} {scope_resp.text}")

    # Store the PAT with unique key
    put_resp = requests.post(
        f"{host}/api/2.0/secrets/put",
        headers=headers,
        json={
            "scope": scope_name,
            "key": secret_key,
            "string_value": pat_value,
        },
    )
    if put_resp.status_code != 200:
        raise RuntimeError(f"Failed to store secret: {put_resp.status_code} {put_resp.text}")

    return {"success": True, "scope": scope_name, "key": secret_key}


def create_app(host: str, oauth_token: str, app_name: str, scope_name: str, secret_key: str) -> dict:
    """Create the Databricks App with secret resource via POST /api/2.0/apps."""
    resp = requests.post(
        f"{host}/api/2.0/apps",
        headers={"Authorization": f"Bearer {oauth_token}"},
        json={
            "name": app_name,
            "resources": [
                {
                    "name": "DATABRICKS_TOKEN",
                    "description": "PAT for model serving access",
                    "secret": {
                        "scope": scope_name,
                        "key": secret_key,
                        "permission": "READ",
                    },
                }
            ],
        },
    )
    # 409 means app already exists -- that's fine for re-provisioning
    if resp.status_code == 409:
        return check_existing_app(host, oauth_token, app_name)
    resp.raise_for_status()
    return resp.json()



def deploy_app(
    host: str, oauth_token: str, app_name: str, source_code_path: str
) -> dict:
    """Deploy the app via POST /api/2.0/apps/{name}/deployments."""
    resp = requests.post(
        f"{host}/api/2.0/apps/{app_name}/deployments",
        headers={"Authorization": f"Bearer {oauth_token}"},
        json={"source_code_path": source_code_path},
    )
    resp.raise_for_status()
    return resp.json()


def grant_sp_secret_access(
    host: str, auth_token: str, scope_name: str, sp_id: str
) -> None:
    """Grant the app's service principal READ access on the secret scope."""
    resp = requests.post(
        f"{host}/api/2.0/secrets/acls/put",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={
            "scope": scope_name,
            "principal": sp_id,
            "permission": "READ",
        },
    )
    resp.raise_for_status()


def list_spawned_apps(host: str, oauth_token: str) -> list:
    """List all coding-agents apps (excluding the spawner itself)."""
    resp = requests.get(
        f"{host}/api/2.0/apps",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )
    resp.raise_for_status()
    apps = resp.json().get("apps", [])
    return [
        {
            "name": a["name"],
            "url": a.get("url", ""),
            "creator": a.get("creator", ""),
            "state": a.get("app_status", {}).get("state", "UNKNOWN"),
            "compute": a.get("compute_status", {}).get("state", "UNKNOWN"),
            "created": a.get("create_time", ""),
        }
        for a in apps
        if a["name"].startswith("coding-agents-") and a["name"] != "coding-agents-spawner"
    ]


def check_existing_app(host: str, oauth_token: str, app_name: str) -> dict:
    """Check if an app already exists."""
    resp = requests.get(
        f"{host}/api/2.0/apps/{app_name}",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )
    if resp.status_code == 200:
        data = resp.json()
        return {
            "deployed": True,
            "app_name": app_name,
            "app_url": data.get("url", ""),
            "state": data.get("status", {}).get("state", "UNKNOWN"),
            "service_principal_id": data.get("service_principal_id"),
            "service_principal_client_id": data.get("service_principal_client_id"),
            "service_principal_name": data.get("service_principal_name"),
        }
    return {"deployed": False}


def provision_app(host: str, admin_token: str, pat_value: str) -> dict:
    """Orchestrate the full provisioning flow.

    Resolves the PAT owner's identity via SCIM, then:
    - Uses pat_value for app creation (so the user owns it)
    - Uses admin_token for secret scopes, ACLs, linking, and deploy
    - Stores pat_value as the secret for the spawned app
    """
    # Deploy from shared template — Databricks snapshots the code at deploy time
    source_code_path = "/Workspace/Shared/apps/coding-agents"
    steps = []

    try:
        # Step 0: Resolve PAT owner identity — this determines the app name
        steps.append({"step": 0, "status": "resolving_user", "message": "Verifying your identity..."})
        email = resolve_pat_owner(host, pat_value)
        if not email:
            raise ValueError("Could not resolve PAT owner identity")
        app_name = app_name_from_email(email)
        scope_name = f"{app_name}-secrets"
        secret_key = str(uuid.uuid4())

        # Step 1: Create secret scope and store user's PAT (admin token for scope ops)
        steps.append({"step": 1, "status": "storing_secret", "message": "Storing token in secret scope..."})
        store_pat_in_secret_scope(host, admin_token, app_name, pat_value, secret_key)

        # Step 2: Create app with secret resource using user's PAT so they own it
        steps.append({"step": 2, "status": "creating_app", "message": f"Creating app '{app_name}'..."})
        app_result = create_app(host, pat_value, app_name, scope_name, secret_key)
        sp_client_id = app_result.get("service_principal_client_id", "")

        # Step 3: Grant the app's SP READ access on the secret scope
        if sp_client_id:
            steps.append({"step": 3, "status": "granting_access", "message": "Granting service principal access to secrets..."})
            grant_sp_secret_access(host, admin_token, scope_name, sp_client_id)

        # Step 4: Deploy from shared template
        steps.append({"step": 4, "status": "deploying", "message": "Deploying app..."})
        deploy_app(host, admin_token, app_name, source_code_path)

        app_url = app_result.get("url", app_result.get("app_url", ""))
        steps.append({"step": 5, "status": "complete", "app_url": app_url})

        return {"success": True, "steps": steps, "app_url": app_url, "app_name": app_name}

    except Exception as exc:
        current_step = steps[-1]["step"] if steps else 0
        current_status = steps[-1]["status"] if steps else "unknown"
        return {
            "success": False,
            "error": {
                "step": current_step,
                "status": current_status,
                "message": str(exc),
            },
        }


# --- Flask Routes ---


@app.route("/")
def index():
    """Serve the spawner UI with PAT input and deploy button."""
    email = request.headers.get("X-Forwarded-Email", "unknown")
    app_name = app_name_from_email(email) if email != "unknown" else "coding-agents-you"
    return f"""<!DOCTYPE html>
<html>
<head><title>Coding Agents Spawner</title>
<style>
  body {{ background:#1a1a2e; color:#eee; font-family:sans-serif; text-align:center; padding:40px 20px; }}
  .container {{ max-width:520px; margin:0 auto; }}
  h1 {{ margin-bottom:8px; }}
  .subtitle {{ color:#aaa; margin-bottom:32px; }}
  label {{ display:block; text-align:left; margin-bottom:6px; font-size:14px; color:#ccc; }}
  input {{ width:100%; padding:12px; font-size:14px; border:1px solid #444; border-radius:6px;
           background:#2a2a4a; color:#eee; box-sizing:border-box; font-family:monospace; }}
  input:focus {{ outline:none; border-color:#4CAF50; }}
  .help {{ text-align:left; font-size:12px; color:#888; margin-top:4px; margin-bottom:20px; }}
  button {{ padding:14px 48px; font-size:16px; cursor:pointer; background:#4CAF50; color:#fff;
            border:none; border-radius:8px; width:100%; }}
  button:hover {{ background:#45a049; }}
  button:disabled {{ background:#555; cursor:not-allowed; }}
  #status {{ margin-top:24px; text-align:left; white-space:pre-wrap; font-size:13px;
             font-family:monospace; background:#0d0d1a; padding:16px; border-radius:8px; display:none; }}
  .success {{ color:#4CAF50; }}
  .error {{ color:#ff6b6b; }}
  .step {{ color:#aaa; }}
  .apps-section {{ margin-top:48px; text-align:left; }}
  .apps-section h2 {{ font-size:18px; margin-bottom:12px; }}
  table {{ width:100%; border-collapse:collapse; font-size:13px; }}
  th {{ text-align:left; padding:8px; border-bottom:2px solid #444; color:#aaa; font-weight:600; }}
  td {{ padding:8px; border-bottom:1px solid #333; }}
  td a {{ color:#4CAF50; text-decoration:none; }}
  td a:hover {{ text-decoration:underline; }}
  .state-running {{ color:#4CAF50; }}
  .state-other {{ color:#f0ad4e; }}
</style>
</head>
<body>
<div class="container">
  <h1>Coding Agents Spawner</h1>
  <p class="subtitle">Logged in as <strong>{email}</strong></p>

  <label for="pat">Personal Access Token</label>
  <input type="password" id="pat" placeholder="dapi..." autocomplete="off" />
  <p class="help">
    Create a PAT at Settings &rarr; Developer &rarr; Access tokens.<br>
    Your app will be named <strong>{app_name}</strong>.
  </p>

  <button id="btn" onclick="deploy()">Deploy My Coding Agent</button>
  <div id="status"></div>

  <div class="apps-section">
    <h2>Spawned Apps</h2>
    <div id="apps-loading" style="color:#888;">Loading...</div>
    <table id="apps-table" style="display:none;">
      <thead><tr><th>App</th><th>Owner</th><th>State</th><th>Created</th></tr></thead>
      <tbody id="apps-body"></tbody>
    </table>
    <div id="apps-empty" style="display:none; color:#888;">No apps spawned yet.</div>
  </div>
</div>
<script>
async function deploy() {{
  const pat = document.getElementById('pat').value.trim();
  if (!pat) {{ alert('Please enter your Personal Access Token.'); return; }}
  const btn = document.getElementById('btn');
  const status = document.getElementById('status');
  btn.disabled = true;
  btn.textContent = 'Provisioning...';
  status.style.display = 'block';
  status.className = 'step';
  status.textContent = 'Starting provisioning...';
  try {{
    const resp = await fetch('/api/provision', {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ pat: pat }})
    }});
    const data = await resp.json();
    if (data.success) {{
      status.className = 'success';
      status.innerHTML = '&#10003; Deployed successfully!\\n\\n'
        + 'App: ' + data.app_name + '\\n'
        + 'URL: <a href="' + data.app_url + '" style="color:#4CAF50">' + data.app_url + '</a>\\n\\n'
        + data.steps.map(s => s.step + '. ' + (s.message || s.status)).join('\\n');
    }} else {{
      status.className = 'error';
      status.textContent = 'Failed at step ' + data.error.step + ' (' + data.error.status + '):\\n' + data.error.message;
    }}
  }} catch (e) {{
    status.className = 'error';
    status.textContent = 'Request failed: ' + e.message;
  }}
  btn.disabled = false;
  btn.textContent = 'Deploy My Coding Agent';
}}

async function loadApps() {{
  try {{
    const resp = await fetch('/api/apps');
    const data = await resp.json();
    document.getElementById('apps-loading').style.display = 'none';
    if (!data.apps || data.apps.length === 0) {{
      document.getElementById('apps-empty').style.display = 'block';
      return;
    }}
    const tbody = document.getElementById('apps-body');
    data.apps.forEach(a => {{
      const stateClass = a.state === 'RUNNING' ? 'state-running' : 'state-other';
      const created = a.created ? new Date(a.created).toLocaleDateString() : '';
      tbody.innerHTML += '<tr>'
        + '<td><a href="' + a.url + '" target="_blank">' + a.name + '</a></td>'
        + '<td>' + a.creator + '</td>'
        + '<td class="' + stateClass + '">' + a.state + '</td>'
        + '<td>' + created + '</td>'
        + '</tr>';
    }});
    document.getElementById('apps-table').style.display = 'table';
  }} catch(e) {{
    document.getElementById('apps-loading').textContent = 'Failed to load apps.';
  }}
}}
loadApps();
</script>
</body>
</html>"""


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"})


@app.route("/api/status")
def api_status():
    """Check if user already has a deployed instance."""
    email = request.headers.get("X-Forwarded-Email", "")
    host = DATABRICKS_HOST

    app_name = app_name_from_email(email)
    result = check_existing_app(host, ADMIN_TOKEN, app_name)
    return jsonify(result)


@app.route("/api/apps")
def api_list_apps():
    """List all spawned coding-agents apps."""
    host = DATABRICKS_HOST
    if not ADMIN_TOKEN:
        return jsonify({"error": "Admin token not configured"}), 500
    apps = list_spawned_apps(host, ADMIN_TOKEN)
    return jsonify({"apps": apps})


@app.route("/api/provision", methods=["POST"])
def api_provision():
    """Run the full provisioning flow with user-supplied PAT."""
    email = request.headers.get("X-Forwarded-Email", "")
    host = DATABRICKS_HOST

    if not ADMIN_TOKEN:
        return jsonify({"success": False, "error": {"step": 0, "status": "config", "message": "Spawner admin token not configured"}}), 500

    body = request.get_json(silent=True) or {}
    pat_value = body.get("pat", "").strip()

    if not pat_value:
        return jsonify({"success": False, "error": {"step": 0, "status": "validation", "message": "PAT is required"}}), 400

    result = provision_app(host, ADMIN_TOKEN, pat_value)
    status_code = 200 if result["success"] else 500
    return jsonify(result), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
