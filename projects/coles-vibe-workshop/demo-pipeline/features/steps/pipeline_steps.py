"""Step definitions for pipeline BDD tests."""

from __future__ import annotations

import time

from behave import given, when, then
from behave.runner import Context
from databricks.sdk.service.sql import StatementState


def _execute_sql(context: Context, sql: str) -> None:
    """Execute SQL via Statement Execution API and store results."""
    resp = context.workspace.statement_execution.execute_statement(
        warehouse_id=context.warehouse_id,
        statement=sql,
        wait_timeout="30s",
    )
    # Poll if needed
    retries = 0
    while resp.status and resp.status.state in (StatementState.PENDING, StatementState.RUNNING):
        time.sleep(1)
        resp = context.workspace.statement_execution.get_statement(resp.statement_id)
        retries += 1
        if retries > 30:
            raise TimeoutError(f"SQL statement timed out after 30s: {sql[:80]}")

    if resp.status and resp.status.state == StatementState.FAILED:
        error = resp.status.error
        raise RuntimeError(f"SQL failed: {error.message if error else 'unknown'}")

    context.result_columns = [c.name for c in resp.manifest.schema.columns] if resp.manifest else []
    context.result_rows = resp.result.data_array if resp.result and resp.result.data_array else []


# ---------------------------------------------------------------------------
# GIVEN steps
# ---------------------------------------------------------------------------

@given('a connection to the Databricks workspace')
def step_workspace_connection(context: Context) -> None:
    assert context.workspace is not None, "WorkspaceClient not initialized"
    assert context.warehouse_id, "No SQL warehouse found"


@given('the catalog "{catalog}" exists')
def step_catalog_exists(context: Context, catalog: str) -> None:
    _execute_sql(context, f"SELECT 1 FROM system.information_schema.catalogs WHERE catalog_name = '{catalog}'")
    assert len(context.result_rows) > 0, f"Catalog '{catalog}' does not exist"


@given('the schema "{schema}" exists')
def step_schema_exists(context: Context, schema: str) -> None:
    _execute_sql(context, f"SHOW SCHEMAS IN workshop_vibe_coding LIKE '{schema}'")
    assert len(context.result_rows) > 0, f"Schema '{schema}' does not exist"


# ---------------------------------------------------------------------------
# WHEN steps
# ---------------------------------------------------------------------------

@when('I query "{table}"')
def step_query_table(context: Context, table: str) -> None:
    _execute_sql(context, f"SELECT * FROM {table}")


@when('I run SQL "{sql}"')
def step_run_sql(context: Context, sql: str) -> None:
    _execute_sql(context, sql)


# ---------------------------------------------------------------------------
# THEN steps
# ---------------------------------------------------------------------------

@then('the table should have more than {count:d} rows')
def step_row_count_more_than(context: Context, count: int) -> None:
    actual = len(context.result_rows)
    assert actual > count, f"Expected more than {count} rows, got {actual}"


@then('the table should have columns "{columns}"')
def step_has_columns(context: Context, columns: str) -> None:
    expected = [c.strip() for c in columns.split(",")]
    for col in expected:
        assert col in context.result_columns, (
            f"Column '{col}' not found. Available: {context.result_columns}"
        )


@then('the column "{column}" should contain "{value}"')
def step_column_contains(context: Context, column: str, value: str) -> None:
    idx = context.result_columns.index(column)
    values = [row[idx] for row in context.result_rows]
    assert value in values, f"'{value}' not found in column '{column}'. Sample: {values[:5]}"


@then('the column "{column}" should not contain "{value}"')
def step_column_not_contains(context: Context, column: str, value: str) -> None:
    idx = context.result_columns.index(column)
    values = [row[idx] for row in context.result_rows]
    assert value not in values, f"'{value}' unexpectedly found in column '{column}'"


@then('there should be {count:d} distinct values in "{column}"')
def step_distinct_count(context: Context, count: int, column: str) -> None:
    idx = context.result_columns.index(column)
    distinct = set(row[idx] for row in context.result_rows)
    assert len(distinct) == count, f"Expected {count} distinct values in '{column}', got {len(distinct)}: {distinct}"


@then('the column "{column}" should have zero nulls')
def step_no_nulls(context: Context, column: str) -> None:
    idx = context.result_columns.index(column)
    nulls = sum(1 for row in context.result_rows if row[idx] is None)
    assert nulls == 0, f"Column '{column}' has {nulls} null values"


@then('all values in "{column}" should be greater than {threshold:d}')
def step_all_greater_than(context: Context, column: str, threshold: int) -> None:
    idx = context.result_columns.index(column)
    violations = [row[idx] for row in context.result_rows if row[idx] is not None and float(row[idx]) <= threshold]
    assert len(violations) == 0, f"{len(violations)} values in '{column}' <= {threshold}. Sample: {violations[:5]}"


@then('all values in "{column}" should be between {low:d} and {high:d}')
def step_all_between(context: Context, column: str, low: int, high: int) -> None:
    idx = context.result_columns.index(column)
    violations = [
        row[idx] for row in context.result_rows
        if row[idx] is not None and not (low <= float(row[idx]) <= high)
    ]
    assert len(violations) == 0, f"{len(violations)} values in '{column}' outside [{low}, {high}]. Sample: {violations[:5]}"


@then('the minimum value in "{column}" should be before "{date}"')
def step_min_before(context: Context, column: str, date: str) -> None:
    idx = context.result_columns.index(column)
    dates = sorted(row[idx] for row in context.result_rows if row[idx] is not None)
    assert dates[0] < date, f"Minimum date in '{column}' is {dates[0]}, expected before {date}"


@then('the maximum value in "{column}" should be after "{date}"')
def step_max_after(context: Context, column: str, date: str) -> None:
    idx = context.result_columns.index(column)
    dates = sorted(row[idx] for row in context.result_rows if row[idx] is not None)
    assert dates[-1] > date, f"Maximum date in '{column}' is {dates[-1]}, expected after {date}"


@then('the first row "{column}" should be "{value}"')
def step_first_row_value(context: Context, column: str, value: str) -> None:
    assert len(context.result_rows) > 0, "Query returned no rows"
    idx = context.result_columns.index(column)
    actual = context.result_rows[0][idx]
    assert actual == value, f"First row '{column}' is '{actual}', expected '{value}'"
