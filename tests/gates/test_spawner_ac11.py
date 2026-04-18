"""
Gate test for AC-11: Given provisioning completes successfully, then the provision-status
endpoint returns the app URL and a "complete" status.

Updated to match actual zero-PAT M2M implementation. The original PRD tested sync
provision_app() returning the URL directly. The implementation uses async provisioning
where the URL is available via poll endpoint /api/provision-status/<app_name>.
"""

from __future__ import annotations

from unittest import mock


class TestAc11:
    """
    Given provisioning completes successfully, then the provision-status endpoint
    returns the app URL with status "complete".
    """

    def test_ac11_completed_job_returns_app_url(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app, _provision_jobs, _provision_lock

            app.config["TESTING"] = True
            client = app.test_client()

        app_name = "coding-agents-success-test"

        with _provision_lock:
            _provision_jobs[app_name] = {
                "steps": [
                    {"step": 0, "status": "starting", "message": "Provisioning..."},
                    {"step": 1, "status": "creating_app", "message": "Creating app..."},
                    {
                        "step": 2,
                        "status": "granting_access",
                        "message": "Granting SP access...",
                    },
                    {
                        "step": 3,
                        "status": "waiting_for_compute",
                        "message": "Waiting...",
                    },
                    {"step": 4, "status": "deploying", "message": "Deploying..."},
                    {"step": 5, "status": "starting", "message": "Waiting for app..."},
                    {"step": 6, "status": "complete", "message": "App is running!"},
                ],
                "status": "complete",
                "app_url": "https://coding-agents-success-test.databricksapps.com",
                "app_name": app_name,
                "email": "success@example.com",
            }

        try:
            resp = client.get(f"/api/provision-status/{app_name}")

            assert resp.status_code == 200
            data = resp.get_json()

            assert data["found"] is True
            assert data["status"] == "complete"
            assert "app_url" in data
            assert data["app_url"].startswith("https://")
            assert "coding-agents-success-test" in data["app_url"]

            # Last step must be "complete"
            last_step = data["steps"][-1]
            assert last_step["status"] == "complete"
        finally:
            with _provision_lock:
                _provision_jobs.pop(app_name, None)

    def test_ac11_unknown_app_returns_not_found(self):
        """Polling for a non-existent app_name returns found: false."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app

            app.config["TESTING"] = True
            client = app.test_client()

        resp = client.get("/api/provision-status/coding-agents-nonexistent")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["found"] is False
