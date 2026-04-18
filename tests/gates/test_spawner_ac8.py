"""
Gate test for AC-8: Given the app is created, when the spawner deploys,
then POST /api/2.0/apps/{name}/deployments is called with correct source path.
"""

from __future__ import annotations

from unittest import mock


class TestAc8:
    """
    Given the app is created and secrets linked, when the spawner deploys,
    then POST /api/2.0/apps/{name}/deployments is called with the correct
    workspace source path.
    """

    def test_ac8_deployment_triggered_with_source_path(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import deploy_app

        mock_response = mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "deployment_id": "deploy-123",
            "status": {"state": "IN_PROGRESS"},
        }

        with mock.patch(
            "spawner.app.requests.post", return_value=mock_response
        ) as mock_post:
            deploy_app(
                host="https://test.databricks.com",
                oauth_token="fake-oauth-token",
                app_name="coding-agents-david-okeeffe",
                source_code_path="/Workspace/Users/david.okeeffe@company.com/apps/coding-agents-david-okeeffe",
            )

            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            url = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("url", "")
            assert "/api/2.0/apps/coding-agents-david-okeeffe/deployments" in url

            body = call_kwargs[1].get("json", {})
            assert (
                body.get("source_code_path")
                == "/Workspace/Users/david.okeeffe@company.com/apps/coding-agents-david-okeeffe"
            )
