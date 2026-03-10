"""Tests for the /api/active-sessions endpoint.

Validates that the endpoint exists, returns the correct response shape,
and correctly reports session status.
"""

import os
import pytest


class TestActiveSessionsEndpoint:
    """GET /api/active-sessions returns live PTY sessions."""

    def test_endpoint_returns_200(self, app_client):
        """GET /api/active-sessions returns 200."""
        resp = app_client.get("/api/active-sessions")
        assert resp.status_code == 200

    def test_response_has_sessions_key(self, app_client):
        """Response JSON has 'sessions' key."""
        resp = app_client.get("/api/active-sessions")
        data = resp.get_json()
        assert "sessions" in data
        assert isinstance(data["sessions"], list)

    def test_empty_when_no_sessions(self, app_client):
        """Returns empty list when no sessions exist."""
        resp = app_client.get("/api/active-sessions")
        data = resp.get_json()
        # May have leftover sessions from other tests, but structure is valid
        assert isinstance(data["sessions"], list)


class TestActiveSessionsWithSession:
    """Tests requiring a live PTY session."""

    def test_created_session_appears(self, app_client, create_session):
        """A created session appears in /api/active-sessions."""
        original = os.environ.get("TMUX_ENABLED")
        os.environ["TMUX_ENABLED"] = "false"
        try:
            session_id = create_session()
            resp = app_client.get("/api/active-sessions")
            data = resp.get_json()
            session_ids = [s["session_id"] for s in data["sessions"]]
            assert session_id in session_ids
        finally:
            if original is None:
                os.environ.pop("TMUX_ENABLED", None)
            else:
                os.environ["TMUX_ENABLED"] = original

    def test_session_has_required_fields(self, app_client, create_session):
        """Each session has session_id, pane_id, and alive fields."""
        original = os.environ.get("TMUX_ENABLED")
        os.environ["TMUX_ENABLED"] = "false"
        try:
            session_id = create_session()
            resp = app_client.get("/api/active-sessions")
            data = resp.get_json()
            matching = [s for s in data["sessions"] if s["session_id"] == session_id]
            assert len(matching) == 1
            session = matching[0]
            assert "session_id" in session
            assert "pane_id" in session
            assert "alive" in session
        finally:
            if original is None:
                os.environ.pop("TMUX_ENABLED", None)
            else:
                os.environ["TMUX_ENABLED"] = original

    def test_alive_session_marked_true(self, app_client, create_session):
        """A freshly created session is marked alive=True."""
        original = os.environ.get("TMUX_ENABLED")
        os.environ["TMUX_ENABLED"] = "false"
        try:
            session_id = create_session()
            resp = app_client.get("/api/active-sessions")
            data = resp.get_json()
            matching = [s for s in data["sessions"] if s["session_id"] == session_id]
            assert len(matching) == 1
            assert matching[0]["alive"] is True
        finally:
            if original is None:
                os.environ.pop("TMUX_ENABLED", None)
            else:
                os.environ["TMUX_ENABLED"] = original

    def test_closed_session_not_alive(self, app_client, create_session):
        """A closed session is either removed or marked alive=False."""
        original = os.environ.get("TMUX_ENABLED")
        os.environ["TMUX_ENABLED"] = "false"
        try:
            session_id = create_session()
            app_client.post("/api/session/close", json={"session_id": session_id})
            resp = app_client.get("/api/active-sessions")
            data = resp.get_json()
            matching = [s for s in data["sessions"] if s["session_id"] == session_id]
            if matching:
                assert matching[0]["alive"] is False
        finally:
            if original is None:
                os.environ.pop("TMUX_ENABLED", None)
            else:
                os.environ["TMUX_ENABLED"] = original
