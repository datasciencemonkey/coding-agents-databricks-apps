"""
Gate test for AC-7: Given the app is created with a service principal, when
grant_sp_volume_access() is called, then UC permissions are set for the SP
to read the coda-wheels volume.

Updated to match actual zero-PAT M2M implementation. The original PRD tested
secret linking via PATCH /api/2.0/apps. The implementation grants UC Volume
access to the app's SP instead (no secrets needed).
"""

from __future__ import annotations

from unittest import mock


class TestAc7:
    """
    Given the app is created with a service principal, when grant_sp_volume_access()
    is called, then USE_CATALOG, USE_SCHEMA, and READ_VOLUME are granted.
    """

    def test_ac7_sp_granted_volume_access(self):
        with mock.patch.dict(
            "os.environ",
            {
                "DATABRICKS_HOST": "https://test.databricks.com",
                "WHEELS_VOLUME_CATALOG": "main",
                "WHEELS_VOLUME_SCHEMA": "coda",
                "WHEELS_VOLUME_NAME": "coda-wheels",
            },
        ):
            import importlib
            import spawner.app as spawner_mod

            importlib.reload(spawner_mod)

        mock_response = mock.Mock()
        mock_response.ok = True
        mock_response.status_code = 200

        app_result = {
            "name": "coding-agents-david-okeeffe",
            "service_principal_name": "sp-name-123",
        }

        with mock.patch.object(
            spawner_mod.requests, "patch", return_value=mock_response
        ) as mock_patch:
            spawner_mod.grant_sp_volume_access(
                host="https://test.databricks.com",
                auth_token="fake-admin-token",
                app_result=app_result,
            )

            # Must make 3 PATCH calls: catalog, schema, volume
            assert mock_patch.call_count == 3

            calls = mock_patch.call_args_list

            # Call 1: USE_CATALOG on catalog
            url0 = calls[0][0][0]
            body0 = calls[0][1]["json"]
            assert "/unity-catalog/permissions/catalog/main" in url0
            assert body0["changes"][0]["add"] == ["USE_CATALOG"]
            assert body0["changes"][0]["principal"] == "sp-name-123"

            # Call 2: USE_SCHEMA on schema
            url1 = calls[1][0][0]
            body1 = calls[1][1]["json"]
            assert "/unity-catalog/permissions/schema/main.coda" in url1
            assert body1["changes"][0]["add"] == ["USE_SCHEMA"]

            # Call 3: READ_VOLUME on volume
            url2 = calls[2][0][0]
            body2 = calls[2][1]["json"]
            assert "/unity-catalog/permissions/volume/main.coda.coda-wheels" in url2
            assert body2["changes"][0]["add"] == ["READ_VOLUME"]

    def test_ac7_skips_grant_if_no_sp_name(self):
        """If the app result has no service_principal_name, grants are skipped."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import grant_sp_volume_access

        app_result = {"name": "coding-agents-test", "service_principal_name": ""}

        with mock.patch("spawner.app.requests.patch") as mock_patch:
            grant_sp_volume_access(
                host="https://test.databricks.com",
                auth_token="fake-admin-token",
                app_result=app_result,
            )

            # No grants should be attempted
            mock_patch.assert_not_called()
