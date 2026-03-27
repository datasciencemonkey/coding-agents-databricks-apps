"""Integration test: PATRotator wired into app."""

from unittest import mock


class TestPATRotatorIntegration:

    def test_app_has_pat_rotator(self):
        with mock.patch("app.initialize_app"):
            import app as app_module
        assert hasattr(app_module, "pat_rotator")

    def test_pat_rotator_is_correct_type(self):
        with mock.patch("app.initialize_app"):
            import app as app_module
        from pat_rotator import PATRotator
        assert isinstance(app_module.pat_rotator, PATRotator)
