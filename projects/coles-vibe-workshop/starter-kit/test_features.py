"""
Feature engineering test stubs for Data Science track Lab 1.
Copy to tests/test_features.py before starting.
"""


# ── Lag Features ──────────────────────────────────────────────────────


def test_create_lag_features(spark, sample_retail_csv):
    """Lag features (1, 3, 6, 12 month) are created correctly."""
    # TODO: Create 24 months of data for one state/industry
    # TODO: Apply lag feature function
    # TODO: Assert turnover_lag_1m equals previous month's value
    # TODO: Assert turnover_lag_12m equals same month last year
    # TODO: Assert first 12 rows have null lag_12m (expected)
    pass


# ── Seasonal Features ─────────────────────────────────────────────────


def test_create_seasonal_features(spark, sample_retail_csv):
    """Seasonal indicators extracted correctly from date column."""
    # TODO: Apply seasonal feature function
    # TODO: Assert month_of_year is 1-12
    # TODO: Assert quarter is 1-4
    # TODO: Assert is_december is True only for month 12
    # TODO: Assert is_q4 is True only for months 10-12
    pass


# ── Growth Features ───────────────────────────────────────────────────


def test_create_growth_features(spark, sample_retail_csv):
    """MoM and YoY growth rates computed correctly."""
    # TODO: Create 24 months of data with known values
    # TODO: Apply growth feature function
    # TODO: Assert turnover_mom_growth = (current - previous) / previous * 100
    # TODO: Assert turnover_yoy_growth = (current - 12m_ago) / 12m_ago * 100
    pass


# ── Feature Table Schema ─────────────────────────────────────────────


def test_feature_table_schema(spark):
    """Feature table has all expected columns."""
    expected_columns = {
        "state", "industry", "month",
        "turnover_millions",
        "turnover_lag_1m", "turnover_lag_3m", "turnover_lag_6m", "turnover_lag_12m",
        "month_of_year", "quarter", "is_december", "is_q4",
        "turnover_mom_growth", "turnover_yoy_growth", "cpi_yoy_change",
    }
    # TODO: Read or create feature table
    # TODO: Assert all expected columns exist
    pass


def test_feature_table_no_key_nulls(spark):
    """Key columns (state, industry, month, turnover_millions) have no nulls."""
    # TODO: Read feature table
    # TODO: Assert state, industry, month, turnover_millions have zero nulls
    # TODO: Note: lag features CAN have nulls in early rows
    pass
