## Step 11: Deploy Your App

Package and deploy to Databricks Apps.

### Prompt

Paste this into Claude Code:

```
Prepare the app for deployment to Databricks Apps:

1. Make sure app/requirements.txt has all dependencies:
   fastapi
   uvicorn
   databricks-sql-connector
   databricks-sdk
   pydantic

2. Create app/app.yaml with:
   command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

3. Deploy to Databricks Apps:
   cd app
   databricks apps deploy --name grocery-app-TEAM_NAME --source-code-path ./

4. Show me the app URL when deployment completes.

5. Test the deployed app:
   curl <app-url>/health
```

### Expected Result

The app is deployed and accessible at a URL like `https://<workspace>.databricks.com/apps/grocery-app-TEAM_NAME`. The health endpoint returns `{"status": "ok"}`.

### If It Doesn't Work

- **Deploy fails:** Check `app.yaml` syntax. Compare with `starter-kit/app.yaml.template`.
- **App starts but shows errors:** Check app logs in the Databricks UI under Apps.
- **Can't connect to database:** Ensure `DATABRICKS_HOST` and `DATABRICKS_HTTP_PATH` are in `app.yaml` env section.
- **502 error after deploy:** The app may still be starting. Wait 30 seconds and refresh.

### Prepare Your Demo

You have 3 minutes to show:
1. Your pipeline (show the DAG or table list in Databricks UI)
2. Your app (load it, use the AI feature)
3. Your Genie space (ask a question live)
4. One thing that surprised you
