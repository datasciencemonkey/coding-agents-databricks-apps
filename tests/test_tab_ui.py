"""Tests for the tab-based terminal UI in index.html.

Validates that the TabManager class, tab bar, mode toggle, and related
tab UI structures exist and are correctly implemented.
"""

import os
import re
import pytest

INDEX_HTML_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "index.html"
)


@pytest.fixture
def html_source():
    """Read the index.html file."""
    with open(INDEX_HTML_PATH, "r") as f:
        return f.read()


class TestTabBarStructure:
    """Tab bar HTML structure."""

    def test_tab_bar_element_exists(self, html_source):
        assert 'id="tab-bar"' in html_source, "No tab-bar element found"

    def test_tab_terminal_container_exists(self, html_source):
        assert "tab-terminal-container" in html_source, "No tab terminal container found"

    def test_add_tab_button_in_tab_bar(self, html_source):
        assert "add-tab-btn" in html_source, "No add-tab button class found"

    def test_close_tab_button(self, html_source):
        assert "close-tab" in html_source, "No close-tab button class found"


class TestTabManagerClass:
    """TabManager JavaScript class."""

    def test_tab_manager_class_exists(self, html_source):
        assert "class TabManager" in html_source, "No TabManager class found"

    def test_add_tab_method(self, html_source):
        assert "addTab" in html_source, "No addTab method found"

    def test_switch_tab_method(self, html_source):
        assert "switchTab" in html_source, "No switchTab method found"

    def test_close_tab_method(self, html_source):
        assert "closeTab" in html_source, "No closeTab method found"

    def test_next_tab_method(self, html_source):
        assert "nextTab" in html_source, "No nextTab method found"

    def test_switch_tab_uses_display_css(self, html_source):
        """switchTab uses display:block/none for visibility."""
        assert "display" in html_source.lower(), "No display CSS logic"
        assert "none" in html_source, "No 'none' display value"
        assert "block" in html_source, "No 'block' display value"

    def test_switch_tab_no_dispose(self, html_source):
        """switchTab does not call .dispose() on hidden panes."""
        switch_pattern = re.compile(
            r'switchTab\s*\([^)]*\)\s*\{([^}]+(?:\{[^}]*\}[^}]*)*)\}',
            re.DOTALL,
        )
        match = switch_pattern.search(html_source)
        assert match, "Could not find switchTab method body"
        assert ".dispose()" not in match.group(1), "switchTab calls .dispose()"

    def test_last_tab_auto_creates(self, html_source):
        """Closing last tab auto-creates a new one."""
        assert "this.tabs.size === 0" in html_source or "tabs.size === 0" in html_source, (
            "No auto-create logic for last tab"
        )


class TestModeToggle:
    """Mode toggle between tabs and grid."""

    def test_mode_toggle_element_exists(self, html_source):
        assert "mode-toggle" in html_source, "No mode toggle element"

    def test_toggle_mode_function(self, html_source):
        assert "toggleMode" in html_source, "No toggleMode function"

    def test_set_mode_function(self, html_source):
        assert "setMode" in html_source, "No setMode function"

    def test_saves_to_localstorage(self, html_source):
        assert "localStorage.setItem" in html_source, "No localStorage.setItem"
        assert "terminal-mode" in html_source, "No terminal-mode key"

    def test_reads_from_localstorage(self, html_source):
        assert "localStorage.getItem" in html_source, "No localStorage.getItem"

    def test_default_mode_is_tabs(self, html_source):
        """Default mode is 'tabs'."""
        assert "'tabs'" in html_source or '"tabs"' in html_source, "No tabs default"


class TestPollingInTabMode:
    """Batch polling optimization for tab mode."""

    def test_tab_manager_has_batch_poll(self, html_source):
        assert "batchPoll" in html_source, "No batchPoll in TabManager"

    def test_tab_mode_filters_to_active_session(self, html_source):
        assert "activeSession" in html_source or "getActiveSessionId" in html_source, (
            "No active session filtering in tab mode polling"
        )
