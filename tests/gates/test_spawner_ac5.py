"""
Gate test for AC-5: Given the app already exists, when create_app() is called and
receives a 409, then it handles it gracefully by checking the existing app.

Updated to match actual zero-PAT M2M implementation. The original PRD tested 409 on
secret scope creation. The implementation handles 409 on app creation instead.
"""

from __future__ import annotations

import pytest
from unittest import mock


class TestAc5:
    """
    Given the app already exists, when create_app() receives a 409,
    then it handles it gracefully by falling back to check_existing_app().
    """

    def test_ac5_app_409_handled_gracefully(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import create_app

        # Mock POST /api/2.0/apps returning 409 (app already exists)
        mock_409 = mock.Mock()
        mock_409.status_code = 409
        mock_409.ok = False

        # Mock GET /api/2.0/apps/{name} (the fallback check)
        mock_existing = mock.Mock()
        mock_existing.status_code = 200
        mock_existing.ok = True
        mock_existing.json.return_value = {
            "name": "coding-agents-david-okeeffe",
            "url": "https://coding-agents-david-okeeffe.databricksapps.com",
            "app_status": {"state": "RUNNING"},
            "service_principal_id": "sp-123",
            "service_principal_client_id": "sp-client-123",
            "service_principal_name": "sp-name-123",
        }

        with (
            mock.patch("spawner.app.requests.post", return_value=mock_409),
            mock.patch("spawner.app.requests.get", return_value=mock_existing),
        ):
            # Should NOT raise — 409 on app creation is expected for re-provisioning
            result = create_app(
                host="https://test.databricks.com",
                admin_token="fake-admin-token",
                app_name="coding-agents-david-okeeffe",
                owner_email="david.okeeffe@company.com",
            )

            # Must return existing app info
            assert result["deployed"] is True
            assert result["app_name"] == "coding-agents-david-okeeffe"

    def test_ac5_non_409_error_still_raises(self):
        """Errors other than 409 should raise normally."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import create_app

        mock_500 = mock.Mock()
        mock_500.status_code = 500
        mock_500.ok = False
        mock_500.raise_for_status.side_effect = Exception("Internal Server Error")

        with mock.patch("spawner.app.requests.post", return_value=mock_500):
            with pytest.raises(Exception, match="Internal Server Error"):
                create_app(
                    host="https://test.databricks.com",
                    admin_token="fake-admin-token",
                    app_name="coding-agents-test",
                    owner_email="test@example.com",
                )
