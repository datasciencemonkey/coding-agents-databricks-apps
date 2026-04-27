"""Tests for the staleness-marking layer in memory/injector.py.

Mirrors what Claude Code's auto-memory harness does for *its* memory files
(injected `<system-reminder>` tags announcing each memory's age). Without
this signal, an N-week-old memory is presented to the next session with
the same authority as a fresh one — slow-burn correctness risk as memory
volume grows.
"""

from datetime import datetime, timedelta, timezone


class TestAgeLabel:
    """_age_label: compact human-readable age for a created_at timestamp."""

    def _label(self):
        from memory.injector import _age_label
        return _age_label

    # -- Datetime input, various ages --

    def _ago(self, **kwargs):
        return datetime.now(timezone.utc) - timedelta(**kwargs)

    def test_today(self):
        assert self._label()(self._ago(hours=2)) == "today"

    def test_yesterday_is_today_at_under_24h(self):
        # Sub-day deltas all read as "today" — same threshold the function uses.
        assert self._label()(self._ago(hours=23)) == "today"

    def test_days_under_a_week(self):
        assert self._label()(self._ago(days=3)) == "3d ago"

    def test_weeks(self):
        assert self._label()(self._ago(days=10)) == "1w ago"
        assert self._label()(self._ago(days=21)) == "3w ago"

    def test_months(self):
        # 60 days → 2 months under the days // 30 rule.
        assert self._label()(self._ago(days=60)) == "2mo ago"
        assert self._label()(self._ago(days=300)) == "10mo ago"

    def test_years(self):
        assert self._label()(self._ago(days=400)) == "1y ago"

    # -- Naive datetime is treated as UTC (no crash) --

    def test_naive_datetime_treated_as_utc(self):
        # Older Python code paths or hand-built datetimes may lack tzinfo.
        naive = datetime.utcnow() - timedelta(days=5)
        # Strip any tz metadata to simulate a naive datetime in case utcnow gains tz in future.
        naive = naive.replace(tzinfo=None)
        assert self._label()(naive) == "5d ago"

    # -- ISO string input (load_memories returns these) --

    def test_iso_string_input(self):
        iso = (datetime.now(timezone.utc) - timedelta(days=4)).isoformat()
        assert self._label()(iso) == "4d ago"

    def test_iso_naive_string(self):
        # Naive ISO (no offset) — should still parse, treat as UTC.
        naive_iso = (datetime.utcnow() - timedelta(days=2)).isoformat()
        assert self._label()(naive_iso) == "2d ago"

    # -- Defensive: bad input never crashes --

    def test_unparseable_string_returns_age_unknown(self):
        assert self._label()("not a date at all") == "age unknown"

    def test_none_returns_age_unknown(self):
        assert self._label()(None) == "age unknown"

    def test_int_returns_age_unknown(self):
        # Defends against an integer epoch slipping through.
        assert self._label()(12345) == "age unknown"


class TestRenderEmitsStalenessSignals:
    """_render_memory_section embeds both the per-entry age tag AND the
    splice-level 'memories are point-in-time' preamble."""

    def _render(self):
        from memory.injector import _render_memory_section
        return _render_memory_section

    def _mem(self, content="Some memory", mem_type="feedback", days_ago=3, project=None):
        ts = datetime.now(timezone.utc) - timedelta(days=days_ago)
        return {
            "type": mem_type,
            "content": content,
            "project_name": project,
            "created_at": ts.isoformat(),
        }

    def test_age_tag_inline_on_each_memory(self):
        out = self._render()([
            self._mem(content="alpha", days_ago=3),
            self._mem(content="beta", days_ago=20),
        ])
        # Each memory should carry its own age annotation.
        assert "alpha" in out and "3d ago" in out
        assert "beta" in out and "2w ago" in out

    def test_age_tag_format(self):
        out = self._render()([self._mem(content="zeta", days_ago=1)])
        # Check the exact wrapping format so reviewers can rely on it.
        assert "_(1d ago)_" in out

    def test_today_label_when_fresh(self):
        out = self._render()([self._mem(content="just-extracted", days_ago=0)])
        assert "_(today)_" in out
        # And no "Nd ago" form for a fresh entry.
        assert "0d ago" not in out

    def test_project_and_age_tags_coexist(self):
        out = self._render()([
            self._mem(content="x", days_ago=5, project="demo"),
        ])
        # Both annotations should be present, in either order.
        assert "_(project: demo)_" in out
        assert "_(5d ago)_" in out

    def test_preamble_has_verify_instruction(self):
        out = self._render()([self._mem(content="a", days_ago=1)])
        # Key phrases from the preamble — durable signal to the reading model.
        # Each phrase is intentionally short enough to fit within one rendered
        # line so a future line-wrap rebreak doesn't silently break this test.
        assert "point-in-time observations" in out
        assert "Verify against the current" in out
        assert "trust what you observe now" in out

    def test_missing_created_at_renders_age_unknown(self):
        # Defensive — old rows or migrations could lack the field.
        memories = [{
            "type": "user",
            "content": "no timestamp",
            "project_name": None,
        }]
        out = self._render()(memories)
        assert "no timestamp" in out
        assert "age unknown" in out
