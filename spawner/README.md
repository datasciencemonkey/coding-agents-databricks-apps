# Coding Agents Spawner

One-click provisioning of individual [coding-agents](../) Databricks Apps for any developer in your workspace.

## How It Works

A developer visits the spawner UI, pastes their Databricks PAT, and clicks **Deploy**. The spawner:

1. **Resolves identity** — calls SCIM `/Me` with the user's PAT to get their email
2. **Stores the PAT** — creates a secret scope `coding-agents-{user}-secrets` and stores the PAT with a unique UUID key (uses admin token for privileged scope operations)
3. **Creates the app** — `POST /api/2.0/apps` with the user's PAT so they own it; the secret resource (`DATABRICKS_TOKEN`) is included in the creation call
4. **Grants SP access** — gives the app's service principal READ on the secret scope
5. **Deploys** — deploys from the shared template at `/Workspace/Shared/apps/coding-agents`

The spawned app is named `coding-agents-{username}` (derived from email), e.g., `coding-agents-david-okeeffe`.

## Architecture

```
┌─────────────────────┐         ┌──────────────────────────┐
│   Spawner App       │         │  Shared Template         │
│   (this app)        │         │  /Workspace/Shared/apps/ │
│                     │ deploy  │  coding-agents/          │
│  - Admin PAT (env)  ├────────►│  - app.py                │
│  - Provisioning API │         │  - app.yaml              │
│  - Spawned apps list│         │  - requirements.txt      │
└─────────────────────┘         └──────────────────────────┘
         │
         │ creates per-user
         ▼
┌─────────────────────────────┐
│  coding-agents-{user}       │
│  - Owned by user            │
│  - DATABRICKS_TOKEN = PAT   │
│  - Deployed from template   │
└─────────────────────────────┘
```

### Token Model

| Token | Stored in | Used for |
|-------|-----------|----------|
| **Admin PAT** | `coding-agents-spawner-secrets/admin-token` | Secret scope creation, ACLs, deployment |
| **User PAT** | `coding-agents-{user}-secrets/{uuid}` | App creation (ownership), runtime `DATABRICKS_TOKEN` |

The admin PAT requires **workspace admin** privileges (for secret scope creation and ACL management).

The user PAT should have **all access** scopes since Claude Code uses it for model serving, workspace operations, Unity Catalog, clusters, etc.

## Prerequisites

- Databricks CLI configured with a profile (`databricks configure --profile <name>`)
- Workspace admin access (for the admin PAT)
- Shared template synced to `/Workspace/Shared/apps/coding-agents`

## Deploy

### First time

```bash
cd spawner
make deploy PROFILE=daveok ADMIN_PAT=dapi...
```

This will:
- Create the `coding-agents-spawner` app
- Create secret scope and store the admin PAT
- Sync the coding-agents template to the shared workspace path
- Sync the spawner source and deploy
- Wait for the app to be RUNNING and print the URL

If you omit `ADMIN_PAT`, it will prompt interactively.

### Subsequent deploys

```bash
make redeploy PROFILE=daveok
```

Syncs source and redeploys (skips secret setup and template sync).

### Other targets

```bash
make status PROFILE=daveok    # Check app status
make logs PROFILE=daveok      # Tail app logs
make sync-template PROFILE=daveok  # Re-sync shared template
make clean PROFILE=daveok     # Remove secret scope (destructive)
make help                     # Show all targets
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Spawner UI |
| `/health` | GET | Health check |
| `/api/status` | GET | Check if current user has a deployed app |
| `/api/apps` | GET | List all spawned coding-agents apps |
| `/api/provision` | POST | Provision a new app (body: `{"pat": "dapi..."}`) |

## Files

```
spawner/
├── app.py            # Flask app with provisioning logic
├── app.yaml          # Databricks App config (exposes ADMIN_TOKEN env)
├── requirements.txt  # flask, gunicorn, requests
├── Makefile          # Deploy/manage targets
└── README.md         # This file
```
