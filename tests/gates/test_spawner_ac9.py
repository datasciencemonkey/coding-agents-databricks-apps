"""
Gate test for AC-9: Given the user already has a deployed instance, when they visit
the spawner, then it shows existing app URL and status.
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


class TestAc9:
    """
    Given the user already has a deployed instance, when they visit the spawner,
    then it shows the existing app URL and status instead of the deploy button.
    """

    def test_ac9_existing_instance_shown(self):
        client = _get_spawner_client()

        # Mock both get_admin_token (called first in route) and check_existing_app
        with (
            mock.patch("spawner.app.get_admin_token", return_value="fake-admin-token"),
            mock.patch("spawner.app.check_existing_app") as mock_check,
        ):
            mock_check.return_value = {
                "deployed": True,
                "app_name": "coding-agents-david-okeeffe",
                "app_url": "https://coding-agents-david-okeeffe-123.databricksapps.com",
                "state": "RUNNING",
            }

            resp = client.get(
                "/api/status",
                headers={
                    "X-Forwarded-Access-Token": "fake-oauth-token",
                    "X-Forwarded-Email": "david.okeeffe@company.com",
                },
            )

            assert resp.status_code == 200
            data = resp.get_json()
            assert data["deployed"] is True
            assert "app_url" in data
            assert "coding-agents-david-okeeffe" in data["app_name"]
