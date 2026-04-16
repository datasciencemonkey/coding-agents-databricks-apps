"""
API test stubs for Lab 2.
These define WHAT the FastAPI backend should do. The agent implements the code to make them pass.
Copy to tests/test_app.py before starting Lab 2.

NOTE: Install httpx first: pip install httpx
"""

import pytest

# TODO: Uncomment these imports once app.py exists
# from httpx import AsyncClient, ASGITransport
# from app import app


# ── Health ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_health_endpoint():
    """GET /health returns 200 with {"status": "ok"}."""
    # TODO: Create AsyncClient with ASGITransport(app=app)
    # TODO: GET /health
    # TODO: Assert status 200
    # TODO: Assert response JSON == {"status": "ok"}
    pass


# ── Metrics ───────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_metrics_valid():
    """GET /api/metrics returns a list of records."""
    # TODO: GET /api/metrics
    # TODO: Assert status 200
    # TODO: Assert response is a list
    # TODO: Assert each record has keys: state, industry, month, turnover_millions, yoy_growth_pct
    pass


@pytest.mark.asyncio
async def test_get_metrics_with_state_filter():
    """GET /api/metrics?state=NSW filters results to NSW only."""
    # TODO: GET /api/metrics?state=New South Wales
    # TODO: Assert status 200
    # TODO: Assert all records have state == "New South Wales"
    pass


@pytest.mark.asyncio
async def test_get_metrics_invalid_date():
    """GET /api/metrics with invalid date format returns 400."""
    # TODO: GET /api/metrics?start_date=not-a-date
    # TODO: Assert status 400 or 422
    pass


# ── Ask AI ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_ask_question_valid():
    """POST /api/ask with a valid question returns answer and sql_query."""
    # TODO: POST /api/ask with {"question": "Which state has the highest turnover?"}
    # TODO: Assert status 200
    # TODO: Assert response has "answer" key (string)
    # TODO: Assert response has "sql_query" key (string)
    pass


@pytest.mark.asyncio
async def test_ask_question_empty():
    """POST /api/ask with empty question returns 400."""
    # TODO: POST /api/ask with {"question": ""}
    # TODO: Assert status 400 or 422
    pass
