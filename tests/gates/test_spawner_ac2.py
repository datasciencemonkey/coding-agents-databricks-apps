"""
Gate test for AC-2: Given a user clicks Deploy, when POST /api/provision is called,
then the spawner starts async provisioning and returns an app_name to poll.

Updated to match actual zero-PAT M2M implementation (async provisioning via background
thread with poll-based progress at /api/provision-status/<app_name>).
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


class TestAc2:
    """
    Given a user clicks Deploy, when POST /api/provision is called,
    then the spawner starts async provisioning and returns app_name for polling.
    """

    def test_ac2_provision_starts_async_and_returns_app_name(self):
        client = _get_spawner_client()

        with (
            mock.patch("spawner.app.get_admin_token", return_value="fake-admin-token"),
            mock.patch(
                "spawner.app.check_existing_app", return_value={"deployed": False}
            ),
            mock.patch("spawner.app.provision_app_async"),
            mock.patch("threading.Thread"),
        ):
            resp = client.post(
                "/api/provision",
                headers={
                    "X-Forwarded-Access-Token": "fake-oauth-token",
                    "X-Forwarded-Email": "david.okeeffe@company.com",
                },
            )

            assert resp.status_code == 200
            data = resp.get_json()

            # Must acknowledge the provision request
            assert data["success"] is True
            assert "app_name" in data
            assert data["app_name"] == "coding-agents-david-okeeffe"

    def test_ac2_provision_returns_already_running_if_app_exists(self):
        client = _get_spawner_client()

        with (
            mock.patch("spawner.app.get_admin_token", return_value="fake-admin-token"),
            mock.patch("spawner.app.check_existing_app") as mock_check,
        ):
            mock_check.return_value = {
                "deployed": True,
                "state": "RUNNING",
                "app_url": "https://coding-agents-david-okeeffe.databricksapps.com",
            }

            resp = client.post(
                "/api/provision",
                headers={
                    "X-Forwarded-Access-Token": "fake-oauth-token",
                    "X-Forwarded-Email": "david.okeeffe@company.com",
                },
            )

            assert resp.status_code == 200
            data = resp.get_json()
            assert data["success"] is True
            assert data["already_running"] is True
            assert "app_url" in data

    def test_ac2_provision_status_returns_steps(self):
        """The poll endpoint returns step-by-step progress from _provision_jobs."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app, _provision_jobs, _provision_lock

            app.config["TESTING"] = True
            client = app.test_client()

        # Simulate an in-progress job
        with _provision_lock:
            _provision_jobs["coding-agents-test-user"] = {
                "steps": [
                    {"step": 0, "status": "starting", "message": "Provisioning..."},
                    {"step": 1, "status": "creating_app", "message": "Creating app..."},
                ],
                "status": "in_progress",
                "app_url": "",
                "app_name": "coding-agents-test-user",
                "email": "test@example.com",
            }

        try:
            resp = client.get("/api/provision-status/coding-agents-test-user")
            assert resp.status_code == 200
            data = resp.get_json()

            assert data["found"] is True
            assert data["status"] == "in_progress"
            assert len(data["steps"]) == 2
            assert data["steps"][-1]["status"] == "creating_app"
        finally:
            with _provision_lock:
                _provision_jobs.pop("coding-agents-test-user", None)
