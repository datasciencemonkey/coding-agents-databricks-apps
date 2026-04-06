"""
Gate test for AC-4: Given a user's email, when create_app() is called, then the spawner
creates the app with owner:{email} in the description field for owner resolution.

Updated to match actual zero-PAT M2M implementation. The original PRD assumed secret
scope creation. The implementation stores owner identity in the app description instead.
"""

from __future__ import annotations

from unittest import mock


class TestAc4:
    """
    Given a user's email, when create_app() is called,
    then the app is created with owner:{email} in the description field.
    """

    def test_ac4_create_app_sets_owner_in_description(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import create_app

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {
            "name": "coding-agents-david-okeeffe",
            "description": "owner:david.okeeffe@company.com",
            "url": "https://coding-agents-david-okeeffe.databricksapps.com",
            "service_principal_id": "sp-123",
            "service_principal_client_id": "sp-client-123",
            "service_principal_name": "sp-name-123",
        }
        mock_response.raise_for_status = mock.Mock()

        with mock.patch(
            "spawner.app.requests.post", return_value=mock_response
        ) as mock_post:
            create_app(
                host="https://test.databricks.com",
                admin_token="fake-admin-token",
                app_name="coding-agents-david-okeeffe",
                owner_email="david.okeeffe@company.com",
            )

            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args

            # Verify the API call target
            url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("url", "")
            assert "/api/2.0/apps" in url

            # Verify the request body sets owner in description
            body = call_kwargs[1].get("json", {})
            assert body["name"] == "coding-agents-david-okeeffe"
            assert body["description"] == "owner:david.okeeffe@company.com"

            # Verify auth header
            headers = call_kwargs[1].get("headers", {})
            assert headers["Authorization"] == "Bearer fake-admin-token"

    def test_ac4_create_app_uses_admin_token_not_user_token(self):
        """The admin SP token is used, not the user's OAuth token — zero-PAT design."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import create_app

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.ok = True
        mock_response.json.return_value = {"name": "coding-agents-test"}
        mock_response.raise_for_status = mock.Mock()

        with mock.patch(
            "spawner.app.requests.post", return_value=mock_response
        ) as mock_post:
            create_app(
                host="https://test.databricks.com",
                admin_token="admin-sp-token",
                app_name="coding-agents-test",
                owner_email="test@example.com",
            )

            headers = mock_post.call_args[1].get("headers", {})
            # Must use the admin SP token, not a user token
            assert "admin-sp-token" in headers["Authorization"]
