"""
Gate test for AC-6: Given a user's email, when app_name_from_email() is called,
then it derives coding-agents-{username} and handles long names with hash truncation.

This AC had no test file in the original auto-generation. Added to cover the
app naming convention including the 63-char limit with hash suffix.
"""

from __future__ import annotations

from unittest import mock


class TestAc6:
    """
    Given a user's email, when app_name_from_email() is called,
    then it derives the app name as coding-agents-{username}.
    """

    def test_ac6_app_name_derived_from_email(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app_name_from_email

        assert (
            app_name_from_email("david.okeeffe@company.com")
            == "coding-agents-david-okeeffe"
        )

    def test_ac6_dots_and_underscores_become_hyphens(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app_name_from_email

        assert app_name_from_email("john_doe@example.com") == "coding-agents-john-doe"
        assert (
            app_name_from_email("first.last@example.com") == "coding-agents-first-last"
        )

    def test_ac6_long_email_truncated_with_hash(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app_name_from_email, MAX_APP_NAME_LENGTH

        # Create an email that would exceed 63 chars
        long_username = "a" * 60  # coding-agents- (14) + 60 = 74 > 63
        result = app_name_from_email(f"{long_username}@example.com")

        assert len(result) <= MAX_APP_NAME_LENGTH
        assert result.startswith("coding-agents-")
        # Should have a hash suffix for uniqueness
        assert len(result.split("-")[-1]) == 6  # sha256[:6]

    def test_ac6_email_lowercased(self):
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app_name_from_email

        assert (
            app_name_from_email("David.OKeeffe@Company.com")
            == "coding-agents-david-okeeffe"
        )

    def test_ac6_deterministic(self):
        """Same email always produces the same app name."""
        with mock.patch.dict(
            "os.environ", {"DATABRICKS_HOST": "https://test.databricks.com"}
        ):
            from spawner.app import app_name_from_email

        name1 = app_name_from_email("user@example.com")
        name2 = app_name_from_email("user@example.com")
        assert name1 == name2
