"""
BDD step definitions for DS feature engineering.
Runs locally without Spark — tests the pure Python logic.
"""
from datetime import date
from behave import given, when, then
import pytest


# ── Import feature functions from test_features_local ─────────────
# In real usage, teams would import from their src/ module.
# Here we inline the functions to keep the BDD test self-contained.

def create_lag_features(values, lag):
    return [None if i < lag else values[i - lag] for i in range(len(values))]


def extract_seasonal_features(d):
    month = d.month
    quarter = (month - 1) // 3 + 1
    return {
        "month_of_year": month,
        "quarter": quarter,
        "is_december": month == 12,
        "is_q4": quarter == 4,
    }


def calc_mom_growth(current, previous):
    if previous is None or previous == 0:
        return None
    return ((current - previous) / previous) * 100


def calc_yoy_growth(current, year_ago):
    if year_ago is None or year_ago == 0:
        return None
    return ((current - year_ago) / year_ago) * 100


def build_feature_row(state, industry, month, turnover, lag_values, cpi_yoy_change=None):
    seasonal = extract_seasonal_features(month)
    return {
        "state": state, "industry": industry, "month": month,
        "turnover_millions": turnover,
        "turnover_lag_1m": lag_values.get("lag_1m"),
        "turnover_lag_3m": lag_values.get("lag_3m"),
        "turnover_lag_6m": lag_values.get("lag_6m"),
        "turnover_lag_12m": lag_values.get("lag_12m"),
        **seasonal,
        "turnover_mom_growth": calc_mom_growth(turnover, lag_values.get("lag_1m")),
        "turnover_yoy_growth": calc_yoy_growth(turnover, lag_values.get("lag_12m")),
        "cpi_yoy_change": cpi_yoy_change,
    }


# ── Background Steps ─────────────────────────────────────────────

@given("a time series of monthly retail turnover data")
def step_create_time_series(context):
    context.values = [4000 + i * 25 for i in range(24)]


@given("the data covers at least 24 months")
def step_verify_length(context):
    assert len(context.values) >= 24


# ── Lag Feature Steps ────────────────────────────────────────────

@when("I create lag features with windows 1, 3, 6, and 12 months")
def step_create_lags(context):
    context.lag_1 = create_lag_features(context.values, 1)
    context.lag_3 = create_lag_features(context.values, 3)
    context.lag_6 = create_lag_features(context.values, 6)
    context.lag_12 = create_lag_features(context.values, 12)


@then("lag_1m equals the previous month value")
def step_check_lag_1(context):
    for i in range(1, len(context.values)):
        assert context.lag_1[i] == context.values[i - 1]


@then("lag_12m equals the same month last year")
def step_check_lag_12(context):
    for i in range(12, len(context.values)):
        assert context.lag_12[i] == context.values[i - 12]


@then("the first 12 rows have null lag_12m")
def step_check_lag_12_nulls(context):
    for i in range(12):
        assert context.lag_12[i] is None


# ── Seasonal Feature Steps ───────────────────────────────────────

@when("I extract seasonal features from the date column")
def step_extract_seasonal(context):
    context.seasonal = [
        extract_seasonal_features(date(2024, m, 1)) for m in range(1, 13)
    ]


@then("month_of_year ranges from 1 to 12")
def step_check_month_range(context):
    months = [s["month_of_year"] for s in context.seasonal]
    assert months == list(range(1, 13))


@then("quarter ranges from 1 to 4")
def step_check_quarter_range(context):
    quarters = sorted(set(s["quarter"] for s in context.seasonal))
    assert quarters == [1, 2, 3, 4]


@then("is_december is true only for month 12")
def step_check_december(context):
    for s in context.seasonal:
        assert s["is_december"] == (s["month_of_year"] == 12)


@then("is_q4 is true only for months 10, 11, 12")
def step_check_q4(context):
    for s in context.seasonal:
        assert s["is_q4"] == (s["month_of_year"] >= 10)


# ── Growth Feature Steps ─────────────────────────────────────────

@given("turnover this month is {current:g} and last month was {previous:g}")
def step_set_turnover(context, current, previous):
    context.current = current
    context.previous = previous


@given("turnover 12 months ago was {year_ago:g}")
def step_set_year_ago(context, year_ago):
    context.year_ago = year_ago


@when("I calculate growth features")
def step_calc_growth(context):
    context.mom = calc_mom_growth(context.current, context.previous)
    context.yoy = calc_yoy_growth(context.current, context.year_ago)


@then("MoM growth is approximately {expected:g} percent")
def step_check_mom(context, expected):
    assert abs(context.mom - expected) < 0.1


@then("YoY growth is approximately {expected:g} percent")
def step_check_yoy(context, expected):
    assert abs(context.yoy - expected) < 0.1


# ── Schema Steps ─────────────────────────────────────────────────

@when("I assemble a complete feature row")
def step_assemble_row(context):
    context.row = build_feature_row(
        "New South Wales", "Food retailing", date(2024, 6, 1), 4600.0,
        {"lag_1m": 4500, "lag_3m": 4400, "lag_6m": 4300, "lag_12m": 4200},
        cpi_yoy_change=3.5,
    )


@then("the row contains {columns}")
def step_check_columns(context, columns):
    cols = [c.strip() for c in columns.split(",")]
    for col in cols:
        assert col in context.row, f"Missing column: {col}"


# ── Null Check Steps ─────────────────────────────────────────────

@when("I assemble a feature row with valid inputs")
def step_assemble_valid_row(context):
    context.row = build_feature_row(
        "Victoria", "Food retailing", date(2024, 3, 1), 3900.0,
        {"lag_1m": 3800},
    )


@then("{column} is not null")
def step_check_not_null(context, column):
    assert context.row[column] is not None
