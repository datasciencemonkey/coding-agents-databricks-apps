## Step 7: Build Prediction App

### Prompt

```
Build a simple prediction web app:

1. FastAPI backend (app/app.py):
   - GET /health → {"status": "ok"}
   - POST /predict:
     - Accepts: {"state": "New South Wales", "industry": "Food retailing", "month": "2024-06"}
     - Looks up latest features for that state/industry from the feature table
     - Calls our Model Serving endpoint with the features
     - Returns: {"predicted_turnover": 4650.2, "state": "New South Wales", "industry": "Food retailing", "month": "2024-06"}
   - GET / → serves the frontend

2. HTML frontend (app/static/index.html):
   - Tailwind CSS + htmx (CDN, no build step)
   - Dark header: "Grocery Forecast — TEAM_NAME"
   - Form with dropdowns: State, Industry, Month
   - Submit button that calls POST /predict via htmx
   - Result card showing the prediction
   - Simple and clean — don't over-engineer

3. Create app/app.yaml:
   command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

4. Create app/requirements.txt:
   fastapi, uvicorn, databricks-sdk, databricks-sql-connector, pydantic

5. Deploy: databricks apps deploy --name grocery-forecast-TEAM_NAME --source-code-path ./app/

Show me the deployed app URL.
```

### Expected Result

A deployed app where you select state/industry/month and get a turnover prediction.

### If It Doesn't Work

- **App can't reach endpoint:** Use the workspace-internal serving URL, not external
- **CORS errors:** Add CORSMiddleware to FastAPI
- **502 after deploy:** App may still be starting. Wait 30 seconds.
- **Feature lookup fails:** Check feature table name and that features exist for the selected state/industry
