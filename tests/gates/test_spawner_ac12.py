"""
Gate test for AC-12 (Manual): Given a fresh workspace user opens the spawner,
clicks Deploy, and waits, then a fully functional coding-agents app is accessible
at the returned URL within 60 seconds.
"""

from __future__ import annotations

import pytest


class TestAc12:
    """Manual verification: full end-to-end provisioning in live workspace."""

    @pytest.mark.skip(
        reason="Requires live Databricks workspace with fresh user account"
    )
    def test_ac12_manual_e2e_provision(self):
        """Manual: deploy spawner, open as fresh user, click Deploy, verify coding-agents app is accessible."""
        pass
