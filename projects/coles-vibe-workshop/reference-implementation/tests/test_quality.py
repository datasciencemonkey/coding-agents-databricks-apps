"""
Data quality tests for the Grocery Intelligence Platform.

These tests verify data quality expectations that would be enforced
by @dp.expect() in the Lakeflow pipeline. They run against the
PySpark fixtures to validate the quality rules independently.

Structure: Given-When-Then with concrete Australian data values.
"""

from datetime import date

from pyspark.sql import functions as F
from pyspark.sql.types import (
    DateType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)


# ═══════════════════════════════════════════════════════════════════════
# RETAIL TURNOVER QUALITY
# ═══════════════════════════════════════════════════════════════════════


class TestRetailTurnoverQuality:
    """Data quality rules for retail turnover data."""

    def test_retail_turnover_positive(self, spark, sample_gold_retail):
        """All turnover values must be strictly positive (> 0)."""
        # Given: gold retail summary data with Australian state turnover figures
        df = sample_gold_retail

        # When: we check for non-positive turnover values
        non_positive = df.filter(F.col("turnover_millions") <= 0).count()

        # Then: no rows have zero or negative turnover
        assert non_positive == 0, (
            f"Found {non_positive} rows with non-positive turnover. "
            "All retail turnover figures should be > 0"
        )

    def test_retail_turnover_reasonable_range(self, spark, sample_gold_retail):
        """Turnover values fall within a reasonable range for Australian retail (0-50000 million AUD)."""
        # Given: gold retail summary data
        df = sample_gold_retail

        # When: we check for out-of-range values
        out_of_range = df.filter(
            (F.col("turnover_millions") < 0) | (F.col("turnover_millions") > 50000)
        ).count()

        # Then: all values are within expected bounds
        assert out_of_range == 0, (
            f"Found {out_of_range} rows with turnover outside 0-50000M range. "
            "Australian monthly state retail turnover should be within this range."
        )

    def test_retail_rolling_averages_positive(self, spark, sample_gold_retail):
        """Rolling averages must be positive when turnover is positive."""
        # Given: gold retail summary with rolling averages
        df = sample_gold_retail

        # When: we check rolling average values
        non_positive_3m = df.filter(
            (F.col("turnover_3m_avg").isNotNull()) & (F.col("turnover_3m_avg") <= 0)
        ).count()
        non_positive_12m = df.filter(
            (F.col("turnover_12m_avg").isNotNull()) & (F.col("turnover_12m_avg") <= 0)
        ).count()

        # Then: rolling averages are positive where they exist
        assert non_positive_3m == 0, "3-month rolling average should be positive"
        assert non_positive_12m == 0, "12-month rolling average should be positive"

    def test_retail_yoy_growth_reasonable(self, spark, sample_gold_retail):
        """YoY growth percentage is within a reasonable range (-100% to 500%)."""
        # Given: gold retail summary with YoY growth
        df = sample_gold_retail

        # When: we check for extreme growth values
        extreme_growth = df.filter(
            (F.col("yoy_growth_pct").isNotNull())
            & ((F.col("yoy_growth_pct") < -100) | (F.col("yoy_growth_pct") > 500))
        ).count()

        # Then: no extreme values
        assert extreme_growth == 0, (
            f"Found {extreme_growth} rows with YoY growth outside -100% to 500% range"
        )


# ═══════════════════════════════════════════════════════════════════════
# DATE QUALITY
# ═══════════════════════════════════════════════════════════════════════


class TestDateQuality:
    """Data quality rules for date columns across all tables."""

    def test_dates_in_range_retail(self, spark, sample_gold_retail):
        """All retail dates fall between 2010 and 2026."""
        # Given: gold retail data with dates
        df = sample_gold_retail

        # When: we check date ranges
        out_of_range = df.filter(
            (F.col("date") < date(2010, 1, 1)) | (F.col("date") > date(2026, 12, 31))
        ).count()

        # Then: all dates are within expected range
        assert out_of_range == 0, (
            f"Found {out_of_range} rows with dates outside 2010-2026 range. "
            "ABS data should only contain dates from 2010 onwards."
        )

    def test_dates_in_range_cpi(self, spark, sample_gold_cpi):
        """All CPI dates fall between 2010 and 2026."""
        # Given: gold CPI data with dates
        df = sample_gold_cpi

        # When: we check date ranges
        out_of_range = df.filter(
            (F.col("date") < date(2010, 1, 1)) | (F.col("date") > date(2026, 12, 31))
        ).count()

        # Then: all dates are within expected range
        assert out_of_range == 0, (
            f"Found {out_of_range} rows with dates outside 2010-2026 range"
        )

    def test_dates_are_date_type_retail(self, spark, sample_gold_retail):
        """Date column in retail data is proper DateType, not a string."""
        # Given: gold retail data
        df = sample_gold_retail

        # When: we inspect the date field type
        date_field = [f for f in df.schema.fields if f.name == "date"][0]

        # Then: it's DateType
        assert isinstance(date_field.dataType, DateType), (
            f"date column should be DateType, got {date_field.dataType}"
        )

    def test_dates_are_date_type_cpi(self, spark, sample_gold_cpi):
        """Date column in CPI data is proper DateType, not a string."""
        # Given: gold CPI data
        df = sample_gold_cpi

        # When: we inspect the date field type
        date_field = [f for f in df.schema.fields if f.name == "date"][0]

        # Then: it's DateType
        assert isinstance(date_field.dataType, DateType), (
            f"date column should be DateType, got {date_field.dataType}"
        )

    def test_no_null_dates(self, spark, sample_gold_retail):
        """No null date values in gold tables."""
        # Given: gold retail data
        df = sample_gold_retail

        # When: we check for null dates
        null_dates = df.filter(F.col("date").isNull()).count()

        # Then: no nulls
        assert null_dates == 0, f"Found {null_dates} null date values"


# ═══════════════════════════════════════════════════════════════════════
# DUPLICATE DETECTION
# ═══════════════════════════════════════════════════════════════════════


class TestDuplicateDetection:
    """Data quality rules for detecting duplicate rows."""

    def test_no_duplicate_rows_retail(self, spark, sample_gold_retail):
        """No exact duplicate rows in gold retail summary."""
        # Given: gold retail data
        df = sample_gold_retail
        total_count = df.count()

        # When: we remove duplicates and count
        distinct_count = df.distinct().count()

        # Then: counts match (no duplicates)
        assert total_count == distinct_count, (
            f"Found {total_count - distinct_count} duplicate rows in retail data"
        )

    def test_no_duplicate_rows_cpi(self, spark, sample_gold_cpi):
        """No exact duplicate rows in gold CPI data."""
        # Given: gold CPI data
        df = sample_gold_cpi
        total_count = df.count()

        # When: we remove duplicates and count
        distinct_count = df.distinct().count()

        # Then: counts match
        assert total_count == distinct_count, (
            f"Found {total_count - distinct_count} duplicate rows in CPI data"
        )

    def test_no_duplicate_state_date_combinations_retail(self, spark, sample_gold_retail):
        """No duplicate (state, industry, date) combinations in retail data."""
        # Given: gold retail data
        df = sample_gold_retail
        total_count = df.count()

        # When: we count distinct combinations of key columns
        distinct_keys = df.select("state", "industry", "date").distinct().count()

        # Then: key combinations are unique
        assert total_count == distinct_keys, (
            f"Found {total_count - distinct_keys} duplicate (state, industry, date) combinations"
        )

    def test_no_duplicate_state_date_combinations_cpi(self, spark, sample_gold_cpi):
        """No duplicate (state, index_name, date) combinations in CPI data."""
        # Given: gold CPI data
        df = sample_gold_cpi
        total_count = df.count()

        # When: we count distinct combinations of key columns
        distinct_keys = df.select("state", "index_name", "date").distinct().count()

        # Then: key combinations are unique
        assert total_count == distinct_keys, (
            f"Found {total_count - distinct_keys} duplicate (state, index_name, date) combinations"
        )


# ═══════════════════════════════════════════════════════════════════════
# REGION CODE VALIDATION
# ═══════════════════════════════════════════════════════════════════════


class TestRegionCodeValidation:
    """Data quality rules for region/state validation."""

    VALID_STATES = {
        "New South Wales",
        "Victoria",
        "Queensland",
        "South Australia",
        "Western Australia",
        "Tasmania",
        "Northern Territory",
        "Australian Capital Territory",
    }

    def test_region_codes_valid_retail(self, spark, sample_gold_retail):
        """All state values in retail data are valid Australian states."""
        # Given: gold retail data with decoded state names
        df = sample_gold_retail

        # When: we collect all distinct states
        states = {row.state for row in df.select("state").distinct().collect()}

        # Then: all states are in the valid set
        invalid_states = states - self.VALID_STATES
        assert len(invalid_states) == 0, (
            f"Found invalid state names: {invalid_states}. "
            f"Valid states: {self.VALID_STATES}"
        )

    def test_region_codes_valid_cpi(self, spark, sample_gold_cpi):
        """All state values in CPI data are valid Australian states."""
        # Given: gold CPI data with decoded state names
        df = sample_gold_cpi

        # When: we collect all distinct states
        states = {row.state for row in df.select("state").distinct().collect()}

        # Then: all states are in the valid set
        invalid_states = states - self.VALID_STATES
        assert len(invalid_states) == 0, (
            f"Found invalid state names: {invalid_states}"
        )

    def test_no_numeric_region_codes_retail(self, spark, sample_gold_retail):
        """No numeric region codes remain in gold retail data (all should be decoded)."""
        # Given: gold retail data
        df = sample_gold_retail

        # When: we check for numeric-looking state values
        states = {row.state for row in df.select("state").distinct().collect()}

        # Then: no numeric strings
        numeric_states = {s for s in states if s.isdigit()}
        assert len(numeric_states) == 0, (
            f"Found undecoded numeric region codes: {numeric_states}. "
            "All region codes should be decoded to state names."
        )

    def test_no_null_states(self, spark, sample_gold_retail):
        """No null state values in gold data."""
        # Given: gold retail data
        df = sample_gold_retail

        # When: we check for null states
        null_states = df.filter(F.col("state").isNull()).count()

        # Then: no nulls
        assert null_states == 0, f"Found {null_states} null state values"


# ═══════════════════════════════════════════════════════════════════════
# CPI INDEX QUALITY
# ═══════════════════════════════════════════════════════════════════════


class TestCpiIndexQuality:
    """Data quality rules for CPI index values."""

    def test_cpi_index_positive(self, spark, sample_gold_cpi):
        """All CPI index values must be positive."""
        # Given: gold CPI data
        df = sample_gold_cpi

        # When: we check for non-positive CPI values
        non_positive = df.filter(F.col("cpi_index") <= 0).count()

        # Then: all CPI values are positive
        assert non_positive == 0, (
            f"Found {non_positive} rows with non-positive CPI index values"
        )

    def test_cpi_index_reasonable_range(self, spark, sample_gold_cpi):
        """CPI index values are within a reasonable range (50-300)."""
        # Given: gold CPI data (Australian CPI is typically 100-200 range)
        df = sample_gold_cpi

        # When: we check for out-of-range values
        out_of_range = df.filter(
            (F.col("cpi_index") < 50) | (F.col("cpi_index") > 300)
        ).count()

        # Then: all values are within expected bounds
        assert out_of_range == 0, (
            f"Found {out_of_range} rows with CPI index outside 50-300 range. "
            "Australian CPI index should be within this range."
        )

    def test_cpi_yoy_change_reasonable(self, spark, sample_gold_cpi):
        """YoY CPI change percentage is within a reasonable range (-20% to 30%)."""
        # Given: gold CPI data with YoY change
        df = sample_gold_cpi

        # When: we check for extreme inflation/deflation
        extreme_change = df.filter(
            (F.col("yoy_change_pct").isNotNull())
            & ((F.col("yoy_change_pct") < -20) | (F.col("yoy_change_pct") > 30))
        ).count()

        # Then: no extreme values (Australian food inflation stays within -20% to 30%)
        assert extreme_change == 0, (
            f"Found {extreme_change} rows with YoY CPI change outside -20% to 30% range"
        )
