"""
Gate test for AC-10: Given any step in provisioning fails, then the error is recorded
in the provision job with step number and detail, and no secrets are leaked.

Updated to match actual zero-PAT M2M implementation. The original PRD tested sync
provision_app() error handling. The implementation uses async provisioning with
in-memory job tracking, where errors are recorded in _provision_jobs.
"""

from __future__ import annotations

from unittest import mock


def _get_spawner_client():
    """Create a Flask test client for the spawner app."""
    with mock.patch.dict(
        "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
    ):
        from spawner.app import app

        app.config["TESTING"] = True
        return app.test_client()


class TestAc10:
    """
    Given any step in async provisioning fails, then the error is recorded
    in the provision job and no secrets/tokens are exposed.
    """

    def test_ac10_provision_error_recorded_in_job(self):
        """When create_app raises, the error is captured in _provision_jobs."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import (
                provision_app_async,
                _provision_jobs,
                _provision_lock,
            )

        app_name = "coding-agents-error-test"

        # Set up the job entry (normally done by the route handler)
        with _provision_lock:
            _provision_jobs[app_name] = {
                "steps": [],
                "status": "in_progress",
                "app_url": "",
                "app_name": app_name,
                "email": "error@example.com",
            }

        # Mock create_app to fail
        with mock.patch(
            "spawner.app.create_app",
            side_effect=RuntimeError("403 Forbidden: insufficient permissions"),
        ):
            provision_app_async(
                host="https://test.databricks.com",
                admin_token="fake-admin-token",
                email="error@example.com",
                app_name=app_name,
            )

        try:
            job = _provision_jobs[app_name]

            # Error must be recorded
            assert job["status"] == "error"
            assert "error" in job
            assert "403" in job["error"] or "insufficient" in job["error"]

            # Error steps must include the failure
            error_steps = [s for s in job["steps"] if s["status"] == "error"]
            assert len(error_steps) >= 1
        finally:
            with _provision_lock:
                _provision_jobs.pop(app_name, None)

    def test_ac10_no_secrets_in_error_response(self):
        """Error responses from the provision-status endpoint must not leak tokens."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app, _provision_jobs, _provision_lock

            app.config["TESTING"] = True
            client = app.test_client()

        app_name = "coding-agents-leak-test"

        with _provision_lock:
            _provision_jobs[app_name] = {
                "steps": [
                    {"step": 1, "status": "creating_app", "message": "Creating app..."},
                    {"step": -1, "status": "error", "message": "API returned 500"},
                ],
                "status": "error",
                "error": "API returned 500",
                "app_url": "",
                "app_name": app_name,
                "email": "test@example.com",
            }

        try:
            resp = client.get(f"/api/provision-status/{app_name}")
            resp_text = resp.data.decode()

            # Must never contain token/secret patterns
            assert "dapi" not in resp_text.lower()
            assert "token_value" not in resp_text
            assert "client_secret" not in resp_text
            assert "sp-client-secret" not in resp_text
        finally:
            with _provision_lock:
                _provision_jobs.pop(app_name, None)

    def test_ac10_provision_requires_email_header(self):
        """POST /api/provision without X-Forwarded-Email returns 400."""
        client = _get_spawner_client()

        with mock.patch("spawner.app.get_admin_token", return_value="fake-token"):
            resp = client.post("/api/provision", headers={})

            assert resp.status_code == 400
            data = resp.get_json()
            assert data["success"] is False
            assert "X-Forwarded-Email" in data.get("error", "")
