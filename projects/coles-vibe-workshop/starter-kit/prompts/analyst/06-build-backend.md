## Step 8: Build the Backend

Implement FastAPI to make all API tests pass.

### Prompt

Paste this into Claude Code:

```
Implement the FastAPI backend in app/app.py to pass all tests in tests/test_app.py.

For GET /api/metrics:
- Query workshop_vibe_coding.TEAM_SCHEMA.retail_summary
- Support optional query params: state, start_date, end_date
- Use databricks-sql-connector with parameterized queries
- Return list of records as JSON

For POST /api/ask:
- Take {"question": "..."} in request body
- Send the question to the Foundation Model API with the table schema as context
- The LLM generates a SQL query
- Execute the SQL query against our gold tables
- Return {"answer": "...", "sql_query": "..."}
- Use the Databricks SDK: from databricks.sdk import WorkspaceClient

For GET /health:
- Return {"status": "ok"}

Connection config from environment variables:
- DATABRICKS_HOST (workspace URL)
- DATABRICKS_HTTP_PATH (SQL warehouse path)
- DATABRICKS_TOKEN (PAT token — already set in your environment)

Create app/requirements.txt with all dependencies:
- fastapi
- uvicorn
- databricks-sql-connector
- databricks-sdk
- pydantic

Run tests after implementation: pytest tests/test_app.py -x
Fix any failures.
```

### Expected Result

An `app/app.py` with three endpoints. All 6 API tests pass.

### If It Doesn't Work

- **databricks-sql-connector import error:** Run `pip install databricks-sql-connector`
- **Auth errors:** Check `echo $DATABRICKS_HOST` and `echo $DATABRICKS_TOKEN` are set
- **SQL errors:** Make sure table names match: `workshop_vibe_coding.TEAM_SCHEMA.retail_summary`
- **Foundation Model API errors:** Check the AI Gateway endpoint. Ask the facilitator for the correct URL.
