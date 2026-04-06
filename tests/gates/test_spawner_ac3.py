"""
Gate test for AC-3: Given valid SP credentials, when get_admin_token() is called,
then an OAuth M2M token is obtained and cached with refresh-before-expiry logic.

Updated to match actual zero-PAT M2M implementation. The original PRD assumed PAT
minting via the user's OAuth token. The implementation uses the spawner's own service
principal (auto-provisioned by Databricks Apps) for all admin operations.
"""

from __future__ import annotations


from unittest import mock


class TestAc3:
    """
    Given valid SP credentials (DATABRICKS_CLIENT_ID/SECRET),
    when get_admin_token() is called, then it obtains and caches an M2M OAuth token.
    """

    def test_ac3_admin_token_obtained_via_m2m_oauth(self):
        env = {
            "DATABRICKS_HOST": "https://test.databricks.com",
            "DATABRICKS_CLIENT_ID": "sp-client-id",
            "DATABRICKS_CLIENT_SECRET": "sp-client-secret",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            # Force reimport to pick up env vars
            import importlib
            import spawner.app as spawner_mod

            importlib.reload(spawner_mod)

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "oauth-token-123",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = mock.Mock()

        # Reset token cache
        spawner_mod._oauth_token = None
        spawner_mod._oauth_token_expiry = 0

        with mock.patch.object(
            spawner_mod.requests, "post", return_value=mock_response
        ) as mock_post:
            token = spawner_mod.get_admin_token()

            # Must call the OIDC token endpoint
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            url = call_args[0][0] if call_args[0] else call_args[1].get("url", "")
            assert "/oidc/v1/token" in url

            # Must use client_credentials grant
            data = call_args[1].get("data", {})
            assert data["grant_type"] == "client_credentials"
            assert data["client_id"] == "sp-client-id"
            assert data["client_secret"] == "sp-client-secret"

            assert token == "oauth-token-123"

    def test_ac3_admin_token_cached_on_second_call(self):
        env = {
            "DATABRICKS_HOST": "https://test.databricks.com",
            "DATABRICKS_CLIENT_ID": "sp-client-id",
            "DATABRICKS_CLIENT_SECRET": "sp-client-secret",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            import importlib
            import spawner.app as spawner_mod

            importlib.reload(spawner_mod)

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "oauth-token-cached",
            "expires_in": 3600,
        }
        mock_response.raise_for_status = mock.Mock()

        spawner_mod._oauth_token = None
        spawner_mod._oauth_token_expiry = 0

        with mock.patch.object(
            spawner_mod.requests, "post", return_value=mock_response
        ) as mock_post:
            token1 = spawner_mod.get_admin_token()
            token2 = spawner_mod.get_admin_token()

            # Second call should use cache — only one HTTP call total
            assert mock_post.call_count == 1
            assert token1 == token2

    def test_ac3_fallback_to_admin_token_env(self):
        """Falls back to ADMIN_TOKEN when no SP credentials available."""
        env = {
            "DATABRICKS_HOST": "https://test.databricks.com",
            "DATABRICKS_CLIENT_ID": "",
            "DATABRICKS_CLIENT_SECRET": "",
            "ADMIN_TOKEN": "legacy-admin-token",
        }
        with mock.patch.dict("os.environ", env, clear=False):
            import importlib
            import spawner.app as spawner_mod

            importlib.reload(spawner_mod)

            # Must call inside the env mock context so ADMIN_TOKEN is visible
            token = spawner_mod.get_admin_token()
            assert token == "legacy-admin-token"
