## Step 7: Write API Tests

Define what the backend should do before building it.

### Prompt

Paste this into Claude Code:

```
Write pytest tests for the FastAPI backend in tests/test_app.py.
Use httpx AsyncClient with ASGITransport for testing.

Tests to write:

1. test_health_endpoint:
   - GET /health returns 200
   - Response body is {"status": "ok"}

2. test_get_metrics_valid:
   - GET /api/metrics returns 200
   - Response is a list of records
   - Each record has keys: state, industry, month, turnover_millions, yoy_growth_pct

3. test_get_metrics_with_state_filter:
   - GET /api/metrics?state=New%20South%20Wales returns 200
   - All records in response have state == "New South Wales"

4. test_get_metrics_invalid_date:
   - GET /api/metrics?start_date=not-a-date returns 400 or 422

5. test_ask_question_valid:
   - POST /api/ask with {"question": "Which state has the highest turnover?"}
   - Returns 200
   - Response has "answer" (string) and "sql_query" (string)

6. test_ask_question_empty:
   - POST /api/ask with {"question": ""} returns 400 or 422

Write ONLY the tests. Do NOT implement the app yet.
Install httpx if needed: pip install httpx pytest-asyncio
```

### Expected Result

A `tests/test_app.py` with 6 async test functions. All tests fail (no app exists yet).

### If It Doesn't Work

- **Import errors:** Expected — `app.py` doesn't exist yet. The tests define the contract.
- **Agent builds the app:** Say "Stop. Delete the implementation. Tests only."
