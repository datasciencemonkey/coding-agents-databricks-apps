"""
FastAPI application tests for the Grocery Intelligence Platform.

These tests define the SPEC for the web app endpoints.
Written BEFORE implementation — the agent builds code to make these pass.

Uses httpx AsyncClient with ASGITransport for async testing.
"""

import pytest
from httpx import ASGITransport, AsyncClient


# ═══════════════════════════════════════════════════════════════════════
# HEALTH ENDPOINT
# ═══════════════════════════════════════════════════════════════════════


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    @pytest.mark.asyncio
    async def test_health_endpoint_returns_200(self):
        """GET /health returns 200 with status ok."""
        # Given: the FastAPI app is running
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we request the health endpoint
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        # Then: response is 200 with expected JSON
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_endpoint_json_content_type(self):
        """GET /health returns application/json content type."""
        # Given: the FastAPI app
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we request health
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")

        # Then: content type is JSON
        assert "application/json" in response.headers["content-type"]


# ═══════════════════════════════════════════════════════════════════════
# METRICS ENDPOINT
# ═══════════════════════════════════════════════════════════════════════


class TestMetricsEndpoint:
    """Tests for the /api/metrics endpoint."""

    @pytest.mark.asyncio
    async def test_metrics_endpoint_returns_json(self):
        """GET /api/metrics returns 200 with a list of metric records."""
        # Given: the FastAPI app with a database connection
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we request metrics
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/metrics")

        # Then: response is 200 with a JSON list
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list), "Metrics should return a list"

    @pytest.mark.asyncio
    async def test_metrics_endpoint_record_keys(self):
        """Each metric record has required keys: state, industry, month, turnover_millions, yoy_growth_pct."""
        # Given: the FastAPI app
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we request metrics
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/metrics")

        # Then: each record has expected keys
        data = response.json()
        if len(data) > 0:
            required_keys = {"state", "industry", "month", "turnover_millions", "yoy_growth_pct"}
            first_record = data[0]
            assert required_keys.issubset(
                set(first_record.keys())
            ), f"Missing keys: {required_keys - set(first_record.keys())}"

    @pytest.mark.asyncio
    async def test_metrics_endpoint_state_filter(self):
        """GET /api/metrics?state=New+South+Wales filters results to NSW only."""
        # Given: the FastAPI app
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we request metrics filtered by state
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/metrics", params={"state": "New South Wales"})

        # Then: all records are for NSW
        assert response.status_code == 200
        data = response.json()
        for record in data:
            assert record["state"] == "New South Wales", (
                f"Expected NSW only, got {record['state']}"
            )

    @pytest.mark.asyncio
    async def test_metrics_endpoint_invalid_date_returns_error(self):
        """GET /api/metrics with invalid date format returns 400 or 422."""
        # Given: the FastAPI app
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we request metrics with an invalid date
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/metrics", params={"start_date": "not-a-date"})

        # Then: error response
        assert response.status_code in (400, 422), (
            f"Invalid date should return 400 or 422, got {response.status_code}"
        )


# ═══════════════════════════════════════════════════════════════════════
# ASK ENDPOINT
# ═══════════════════════════════════════════════════════════════════════


class TestAskEndpoint:
    """Tests for the /api/ask natural language query endpoint."""

    @pytest.mark.asyncio
    async def test_ask_endpoint_returns_response(self):
        """POST /api/ask with a valid question returns answer and sql_query."""
        # Given: the FastAPI app
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we ask a question about the data
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/ask",
                json={"question": "Which state has the highest retail turnover?"},
            )

        # Then: response has answer and sql_query
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data, "Response should contain 'answer' key"
        assert "sql_query" in data, "Response should contain 'sql_query' key"
        assert isinstance(data["answer"], str), "Answer should be a string"
        assert len(data["answer"]) > 0, "Answer should not be empty"

    @pytest.mark.asyncio
    async def test_ask_endpoint_empty_question_returns_error(self):
        """POST /api/ask with empty question returns 400 or 422."""
        # Given: the FastAPI app
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we send an empty question
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/ask", json={"question": ""})

        # Then: error response
        assert response.status_code in (400, 422), (
            f"Empty question should return 400 or 422, got {response.status_code}"
        )

    @pytest.mark.asyncio
    async def test_ask_endpoint_missing_question_returns_error(self):
        """POST /api/ask without question field returns 422."""
        # Given: the FastAPI app
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we send a request missing the question field
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/api/ask", json={})

        # Then: validation error
        assert response.status_code == 422, (
            f"Missing question should return 422, got {response.status_code}"
        )


# ═══════════════════════════════════════════════════════════════════════
# STATIC FILES
# ═══════════════════════════════════════════════════════════════════════


class TestStaticFiles:
    """Tests for serving the frontend HTML."""

    @pytest.mark.asyncio
    async def test_root_returns_html(self):
        """GET / returns HTML content (the frontend)."""
        # Given: the FastAPI app serving static files
        from app.app import app

        transport = ASGITransport(app=app)

        # When: we request the root
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/")

        # Then: returns HTML
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", ""), (
            "Root should serve HTML content"
        )
        assert "<html" in response.text.lower() or "<!doctype" in response.text.lower(), (
            "Response should contain HTML markup"
        )
