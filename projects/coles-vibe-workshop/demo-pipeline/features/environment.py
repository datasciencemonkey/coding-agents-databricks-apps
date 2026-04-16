"""Behave environment hooks — Databricks workspace connection."""

from __future__ import annotations

from databricks.sdk import WorkspaceClient


def before_all(context):
    """Connect to Databricks workspace."""
    context.workspace = WorkspaceClient()
    context.cursor = None

    # Auto-discover a running SQL warehouse
    warehouses = list(context.workspace.warehouses.list())
    running = [w for w in warehouses if w.state and w.state.value == "RUNNING"]
    if not running:
        raise RuntimeError("No running SQL warehouse found")
    context.warehouse_id = running[0].id


def before_scenario(context, scenario):
    """Get a fresh statement execution connection per scenario."""
    context.result = None
    context.result_columns = []
    context.result_rows = []


def after_all(context):
    """Clean up."""
    pass
