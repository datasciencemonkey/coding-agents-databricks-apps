"""
Gate test for AC-1: Given a user opens the spawner URL, when X-Forwarded-Email
is present, then the spawner shows the user's email and a Deploy button.
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


class TestAc1:
    """
    Given a user opens the spawner URL, when X-Forwarded-Access-Token is present,
    then the spawner shows the user's email and a Deploy button.
    """

    def test_ac1_spawner_shows_user_and_deploy_button(self):
        client = _get_spawner_client()

        # Simulate Databricks Apps injecting OAuth headers
        resp = client.get(
            "/",
            headers={
                "X-Forwarded-Access-Token": "fake-oauth-token",
                "X-Forwarded-Email": "david.okeeffe@company.com",
            },
        )

        assert resp.status_code == 200
        html = resp.data.decode()

        # Page must show user's email
        assert "david.okeeffe@company.com" in html

        # Page must have a deploy button/action
        assert "deploy" in html.lower() or "Deploy" in html
