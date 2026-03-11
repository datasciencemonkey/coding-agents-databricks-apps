# Makefile for deploying Coding Agents Spawner to Databricks Apps
#
# Usage:
#   make deploy PROFILE=daveok ADMIN_PAT=dapi...   # full deploy (first time)
#   make redeploy PROFILE=daveok                    # sync + deploy only
#   make status PROFILE=daveok
#   make logs PROFILE=daveok

PROFILE       ?= DEFAULT
APP_NAME      := coding-agents-spawner
SECRET_SCOPE  := $(APP_NAME)-secrets
SECRET_KEY    := admin-token
TEMPLATE_SRC  := /Workspace/Shared/apps/coding-agents

USER_EMAIL    = $(shell databricks current-user me --profile $(PROFILE) --output json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('userName',''))")
WORKSPACE_PATH = /Workspace/Users/$(USER_EMAIL)/apps/$(APP_NAME)
HOST          = $(shell databricks auth env --profile $(PROFILE) 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['env']['DATABRICKS_HOST'])")
TOKEN         = $(shell databricks auth token --profile $(PROFILE) 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

.PHONY: help run deploy redeploy create-app setup-secret sync-template sync deploy-app status logs clean

run: ## Wait for app to be running and print URL
	@echo "==> Waiting for '$(APP_NAME)' to be running..."
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \
		STATE=$$(databricks apps get $(APP_NAME) --profile $(PROFILE) --output json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('app_status',{}).get('state',''))"); \
		if [ "$$STATE" = "RUNNING" ]; then \
			echo ""; \
			echo "App is RUNNING!"; \
			databricks apps get $(APP_NAME) --profile $(PROFILE) --output json 2>/dev/null | python3 -c "import sys,json; print('URL:', json.load(sys.stdin).get('url','(unknown)'))"; \
			exit 0; \
		fi; \
		echo "    State: $$STATE (waiting...)"; \
		sleep 10; \
	done; \
	echo "    Timed out waiting for app to reach RUNNING state."

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

deploy: create-app setup-secret sync-template sync deploy-app run ## Full deploy: create app, set admin secret, sync template + spawner, deploy + run

redeploy: sync deploy-app run ## Redeploy: sync spawner + deploy (skip secret setup)

create-app: ## Create the spawner app (idempotent)
	@echo "==> Checking if app '$(APP_NAME)' exists..."
	@if databricks apps get $(APP_NAME) --profile $(PROFILE) >/dev/null 2>&1; then \
		echo "    App '$(APP_NAME)' already exists, skipping create."; \
	else \
		echo "    Creating app '$(APP_NAME)'..."; \
		databricks apps create $(APP_NAME) --profile $(PROFILE); \
	fi

setup-secret: ## Create secret scope, store admin PAT, link to app
	@echo "==> Setting up ADMIN_TOKEN secret..."
	@# Create scope if it doesn't exist
	@if databricks secrets list-scopes --profile $(PROFILE) --output json 2>/dev/null | python3 -c "import sys,json; scopes=json.load(sys.stdin); names=[s['name'] for s in (scopes if isinstance(scopes,list) else scopes.get('scopes',[]))]; exit(0 if '$(SECRET_SCOPE)' in names else 1)" 2>/dev/null; then \
		echo "    Secret scope '$(SECRET_SCOPE)' already exists."; \
	else \
		echo "    Creating secret scope '$(SECRET_SCOPE)'..."; \
		databricks secrets create-scope $(SECRET_SCOPE) --profile $(PROFILE); \
	fi
	@# Store the admin PAT
	@if [ -z "$(ADMIN_PAT)" ]; then \
		echo "    Enter the admin PAT (will not echo):"; \
		read -s pat_value && \
		echo "$$pat_value" | databricks secrets put-secret $(SECRET_SCOPE) $(SECRET_KEY) --profile $(PROFILE); \
	else \
		echo "$(ADMIN_PAT)" | databricks secrets put-secret $(SECRET_SCOPE) $(SECRET_KEY) --profile $(PROFILE); \
	fi
	@echo "    Secret stored in $(SECRET_SCOPE)/$(SECRET_KEY)"
	@# Grant spawner SP READ on the scope
	@echo "    Granting spawner SP access..."
	@SP_CLIENT_ID=$$(databricks apps get $(APP_NAME) --profile $(PROFILE) --output json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('service_principal_client_id',''))") && \
	if [ -n "$$SP_CLIENT_ID" ]; then \
		databricks secrets put-acl $(SECRET_SCOPE) $$SP_CLIENT_ID READ --profile $(PROFILE); \
		echo "    Granted READ to $$SP_CLIENT_ID"; \
	else \
		echo "    WARNING: Could not find SP client ID, skipping ACL grant."; \
	fi
	@# Link secret to app resource
	@echo "    Linking secret to app resource 'ADMIN_TOKEN'..."
	@curl -s -X PATCH \
		"$(HOST)/api/2.0/apps/$(APP_NAME)" \
		-H "Authorization: Bearer $(TOKEN)" \
		-H "Content-Type: application/json" \
		-d '{"resources":[{"name":"ADMIN_TOKEN","description":"Admin PAT for provisioning operations","secret":{"scope":"$(SECRET_SCOPE)","key":"$(SECRET_KEY)","permission":"READ"}}]}' \
		>/dev/null
	@echo "    App resource linked."

sync-template: ## Sync coding-agents source to shared template path
	@echo "==> Syncing coding-agents template to $(TEMPLATE_SRC)..."
	@databricks workspace mkdirs /Workspace/Shared/apps --profile $(PROFILE) 2>/dev/null || true
	@cd .. && databricks sync . $(TEMPLATE_SRC) --watch=false --profile $(PROFILE)
	@# Override app.yaml with spawner-friendly defaults (no gateway valueFrom)
	@echo "    Uploading template app.yaml..."
	@printf 'command:\n  - gunicorn\n  - app:app\nenv:\n  - name: HOME\n    value: /app/python/source_code\n  - name: DATABRICKS_TOKEN\n    valueFrom: DATABRICKS_TOKEN\n  - name: ANTHROPIC_MODEL\n    value: databricks-claude-sonnet-4-6\n  - name: GEMINI_MODEL\n    value: databricks-gemini-3-1-pro\n  - name: CLAUDE_CODE_DISABLE_AUTO_MEMORY\n    value: 0\n' | databricks workspace import $(TEMPLATE_SRC)/app.yaml --format AUTO --overwrite --profile $(PROFILE)
	@echo "    Template synced."

sync: ## Sync spawner source to workspace
	@echo "==> Syncing spawner to $(WORKSPACE_PATH)..."
	@databricks sync . $(WORKSPACE_PATH) --watch=false --profile $(PROFILE)

deploy-app: ## Deploy the spawner app
	@echo "==> Deploying '$(APP_NAME)'..."
	@databricks apps deploy $(APP_NAME) --source-code-path $(WORKSPACE_PATH) --profile $(PROFILE) --no-wait
	@echo ""
	@echo "App URL:"
	@databricks apps get $(APP_NAME) --profile $(PROFILE) --output json 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('url','(pending)'))"

status: ## Check spawner app status
	@databricks apps get $(APP_NAME) --profile $(PROFILE)

logs: ## Tail spawner app logs
	@databricks apps logs $(APP_NAME) --profile $(PROFILE)

clean: ## Remove secret scope (destructive)
	@echo "==> Removing secret scope '$(SECRET_SCOPE)'..."
	@databricks secrets delete-scope $(SECRET_SCOPE) --profile $(PROFILE)
