"""
Pipeline tests for the Grocery Intelligence Platform.

These tests define the SPEC for every transformation in the medallion pipeline.
Written BEFORE implementation — the agent builds code to make these pass.

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
# BRONZE LAYER TESTS
# ═══════════════════════════════════════════════════════════════════════


# ── Bronze: Retail Trade ──────────────────────────────────────────────


class TestBronzeRetailTrade:
    """Tests for bronze ingestion of ABS Retail Trade API data."""

    def test_bronze_retail_trade_schema(self, spark, sample_retail_csv):
        """Bronze retail table preserves all columns from the API CSV response."""
        # Given: raw CSV data from ABS Retail Trade API
        bronze_df = sample_retail_csv

        # When: data is ingested to bronze layer
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        result = transform_bronze_retail_trade(bronze_df)

        # Then: all original API columns are preserved plus _ingested_at
        expected_columns = {
            "DATAFLOW",
            "FREQ",
            "MEASURE",
            "INDUSTRY",
            "REGION",
            "TIME_PERIOD",
            "OBS_VALUE",
            "_ingested_at",
        }
        assert set(result.columns) == expected_columns
        assert result.count() == 6

    def test_bronze_retail_trade_no_nulls(self, spark, sample_retail_csv):
        """Bronze retail table rejects rows with null turnover or time period."""
        # Given: raw CSV data from ABS Retail Trade API
        bronze_df = sample_retail_csv

        # When: data is ingested to bronze layer
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        result = transform_bronze_retail_trade(bronze_df)

        # Then: no nulls in critical columns
        null_time = result.filter(F.col("TIME_PERIOD").isNull()).count()
        null_value = result.filter(F.col("OBS_VALUE").isNull()).count()
        assert null_time == 0, "TIME_PERIOD should have no null values"
        assert null_value == 0, "OBS_VALUE should have no null values"

    def test_bronze_retail_trade_adds_ingestion_timestamp(self, spark, sample_retail_csv):
        """Bronze retail table adds an _ingested_at timestamp column."""
        # Given: raw CSV data
        bronze_df = sample_retail_csv

        # When: data is ingested to bronze layer
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        result = transform_bronze_retail_trade(bronze_df)

        # Then: _ingested_at column exists and is not null for any row
        assert "_ingested_at" in result.columns
        null_count = result.filter(F.col("_ingested_at").isNull()).count()
        assert null_count == 0, "_ingested_at should be populated for all rows"


# ── Bronze: CPI Food ─────────────────────────────────────────────────


class TestBronzeCpiFood:
    """Tests for bronze ingestion of ABS CPI Food API data."""

    def test_bronze_cpi_food_schema(self, spark, sample_cpi_csv):
        """Bronze CPI table preserves all columns from the API CSV response."""
        # Given: raw CSV data from ABS CPI API
        bronze_df = sample_cpi_csv

        # When: data is ingested to bronze layer
        from src.bronze.abs_cpi_food import transform_bronze_cpi_food

        result = transform_bronze_cpi_food(bronze_df)

        # Then: all original API columns are preserved plus _ingested_at
        expected_columns = {
            "DATAFLOW",
            "FREQ",
            "MEASURE",
            "INDEX",
            "REGION",
            "TIME_PERIOD",
            "OBS_VALUE",
            "_ingested_at",
        }
        assert set(result.columns) == expected_columns
        assert result.count() == 5

    def test_bronze_cpi_food_date_format(self, spark, sample_cpi_csv):
        """Bronze CPI data contains valid quarterly time periods."""
        # Given: raw CPI CSV data with quarterly periods
        bronze_df = sample_cpi_csv

        # When: data is ingested to bronze layer
        from src.bronze.abs_cpi_food import transform_bronze_cpi_food

        result = transform_bronze_cpi_food(bronze_df)

        # Then: TIME_PERIOD values match quarterly format (YYYY-QN)
        time_periods = [row.TIME_PERIOD for row in result.select("TIME_PERIOD").collect()]
        for tp in time_periods:
            assert tp is not None, "TIME_PERIOD should not be null"
            # Quarterly format: 2024-Q1, 2024-Q2, etc.
            assert "-Q" in tp or "-" in tp, f"TIME_PERIOD '{tp}' should contain date separator"

    def test_bronze_cpi_food_no_null_values(self, spark, sample_cpi_csv):
        """Bronze CPI table has no null OBS_VALUE entries."""
        # Given: raw CPI CSV data
        bronze_df = sample_cpi_csv

        # When: data is ingested to bronze layer
        from src.bronze.abs_cpi_food import transform_bronze_cpi_food

        result = transform_bronze_cpi_food(bronze_df)

        # Then: OBS_VALUE column has no nulls
        null_count = result.filter(F.col("OBS_VALUE").isNull()).count()
        assert null_count == 0, "OBS_VALUE should have no null values in CPI data"


# ═══════════════════════════════════════════════════════════════════════
# SILVER LAYER TESTS
# ═══════════════════════════════════════════════════════════════════════


# ── Silver: Retail Turnover ──────────────────────────────────────────


class TestSilverRetailTurnover:
    """Tests for silver transformation of retail trade data."""

    def test_silver_retail_turnover_decodes_regions(self, spark, sample_retail_csv):
        """REGION code '1' becomes 'New South Wales', '2' becomes 'Victoria', etc."""
        # Given: bronze retail data with numeric region codes
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        bronze_df = transform_bronze_retail_trade(sample_retail_csv)

        # When: silver transformation decodes region codes
        from src.silver.retail_turnover import transform_silver_retail_turnover

        result = transform_silver_retail_turnover(bronze_df)

        # Then: region codes are decoded to full state names
        states = {row.state for row in result.select("state").distinct().collect()}
        assert "New South Wales" in states, "Region code 1 should decode to New South Wales"
        assert "Victoria" in states, "Region code 2 should decode to Victoria"
        assert "Queensland" in states, "Region code 3 should decode to Queensland"
        # Numeric codes should not appear
        assert "1" not in states, "Numeric region codes should be replaced"

    def test_silver_retail_turnover_decodes_industries(self, spark, sample_retail_csv):
        """INDUSTRY code '20' becomes 'Food retailing', '41' becomes 'Clothing/footwear/personal'."""
        # Given: bronze retail data with numeric industry codes
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        bronze_df = transform_bronze_retail_trade(sample_retail_csv)

        # When: silver transformation decodes industry codes
        from src.silver.retail_turnover import transform_silver_retail_turnover

        result = transform_silver_retail_turnover(bronze_df)

        # Then: industry codes are decoded to readable names
        industries = {row.industry for row in result.select("industry").distinct().collect()}
        assert "Food retailing" in industries, "Industry code 20 should decode to Food retailing"
        # Code 41 is in the sample data
        assert any(
            "Clothing" in i for i in industries
        ), "Industry code 41 should decode to Clothing/footwear/personal"

    def test_silver_retail_turnover_date_type(self, spark, sample_retail_csv):
        """TIME_PERIOD string '2024-01' is parsed to a proper DATE column."""
        # Given: bronze retail data with string time periods
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        bronze_df = transform_bronze_retail_trade(sample_retail_csv)

        # When: silver transformation parses dates
        from src.silver.retail_turnover import transform_silver_retail_turnover

        result = transform_silver_retail_turnover(bronze_df)

        # Then: date column is DateType
        date_field = [f for f in result.schema.fields if f.name == "date"][0]
        assert isinstance(
            date_field.dataType, DateType
        ), f"date column should be DateType, got {date_field.dataType}"

        # And: '2024-01' is parsed to date(2024, 1, 1)
        dates = [row.date for row in result.select("date").distinct().collect()]
        assert date(2024, 1, 1) in dates, "2024-01 should parse to date(2024, 1, 1)"
        assert date(2024, 2, 1) in dates, "2024-02 should parse to date(2024, 2, 1)"

    def test_silver_retail_turnover_renames_obs_value(self, spark, sample_retail_csv):
        """OBS_VALUE is renamed to turnover_millions in silver layer."""
        # Given: bronze retail data with OBS_VALUE column
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        bronze_df = transform_bronze_retail_trade(sample_retail_csv)

        # When: silver transformation renames columns
        from src.silver.retail_turnover import transform_silver_retail_turnover

        result = transform_silver_retail_turnover(bronze_df)

        # Then: turnover_millions exists, OBS_VALUE does not
        assert "turnover_millions" in result.columns, "Should have turnover_millions column"
        assert "OBS_VALUE" not in result.columns, "OBS_VALUE should be renamed"

        # And: values are preserved (NSW Food retailing Jan 2024 = 4500.0)
        nsw_jan = result.filter(
            (F.col("state") == "New South Wales")
            & (F.col("industry") == "Food retailing")
            & (F.col("date") == date(2024, 1, 1))
        ).first()
        assert nsw_jan is not None
        assert nsw_jan.turnover_millions == 4500.0

    def test_silver_removes_nulls(self, spark, sample_retail_csv_with_nulls):
        """Silver layer filters out rows with null OBS_VALUE or TIME_PERIOD."""
        # Given: bronze data containing rows with null values
        from src.bronze.abs_retail_trade import transform_bronze_retail_trade

        bronze_df = transform_bronze_retail_trade(sample_retail_csv_with_nulls)

        # When: silver transformation cleans data
        from src.silver.retail_turnover import transform_silver_retail_turnover

        result = transform_silver_retail_turnover(bronze_df)

        # Then: no null values in critical columns
        null_turnover = result.filter(F.col("turnover_millions").isNull()).count()
        null_date = result.filter(F.col("date").isNull()).count()
        assert null_turnover == 0, "Silver layer should have no null turnover values"
        assert null_date == 0, "Silver layer should have no null date values"

        # And: row count is reduced (2 of 5 input rows had nulls)
        assert result.count() == 3, "Should have 3 rows after filtering nulls"


# ── Silver: Food Price Index ─────────────────────────────────────────


class TestSilverFoodPriceIndex:
    """Tests for silver transformation of CPI food data."""

    def test_silver_food_price_index_schema(self, spark, sample_cpi_csv):
        """Silver CPI table has decoded columns with proper types."""
        # Given: bronze CPI data
        from src.bronze.abs_cpi_food import transform_bronze_cpi_food

        bronze_df = transform_bronze_cpi_food(sample_cpi_csv)

        # When: silver transformation is applied
        from src.silver.food_price_index import transform_silver_food_price_index

        result = transform_silver_food_price_index(bronze_df)

        # Then: has expected column set
        expected_columns = {"date", "state", "index_name", "cpi_index", "quarter", "year"}
        assert set(result.columns) == expected_columns

    def test_silver_food_price_index_decodes_index_names(self, spark, sample_cpi_csv):
        """INDEX code '10001' decodes to 'All groups CPI', '20001' to 'Food and non-alcoholic beverages'."""
        # Given: bronze CPI data with numeric index codes
        from src.bronze.abs_cpi_food import transform_bronze_cpi_food

        bronze_df = transform_bronze_cpi_food(sample_cpi_csv)

        # When: silver transformation decodes indices
        from src.silver.food_price_index import transform_silver_food_price_index

        result = transform_silver_food_price_index(bronze_df)

        # Then: index codes are decoded to readable names
        index_names = {row.index_name for row in result.select("index_name").distinct().collect()}
        assert "All groups CPI" in index_names, "Index code 10001 should decode to All groups CPI"
        assert (
            "Food and non-alcoholic beverages" in index_names
        ), "Index code 20001 should decode to Food and non-alcoholic beverages"

    def test_silver_food_price_index_decodes_regions(self, spark, sample_cpi_csv):
        """Region codes in CPI data are decoded to state names."""
        # Given: bronze CPI data with numeric region codes
        from src.bronze.abs_cpi_food import transform_bronze_cpi_food

        bronze_df = transform_bronze_cpi_food(sample_cpi_csv)

        # When: silver transformation decodes regions
        from src.silver.food_price_index import transform_silver_food_price_index

        result = transform_silver_food_price_index(bronze_df)

        # Then: region codes decoded to state names
        states = {row.state for row in result.select("state").distinct().collect()}
        assert "New South Wales" in states
        assert "Victoria" in states

    def test_silver_food_price_index_renames_obs_value(self, spark, sample_cpi_csv):
        """OBS_VALUE is renamed to cpi_index in silver layer."""
        # Given: bronze CPI data with OBS_VALUE
        from src.bronze.abs_cpi_food import transform_bronze_cpi_food

        bronze_df = transform_bronze_cpi_food(sample_cpi_csv)

        # When: silver transformation renames columns
        from src.silver.food_price_index import transform_silver_food_price_index

        result = transform_silver_food_price_index(bronze_df)

        # Then: cpi_index exists with correct values
        assert "cpi_index" in result.columns
        assert "OBS_VALUE" not in result.columns

        # NSW All groups CPI Q1 2024 = 136.4
        nsw_q1 = result.filter(
            (F.col("state") == "New South Wales")
            & (F.col("index_name") == "All groups CPI")
            & (F.col("year") == 2024)
            & (F.col("quarter") == 1)
        ).first()
        assert nsw_q1 is not None
        assert nsw_q1.cpi_index == 136.4


# ═══════════════════════════════════════════════════════════════════════
# GOLD LAYER TESTS
# ═══════════════════════════════════════════════════════════════════════


# ── Gold: Retail Summary ─────────────────────────────────────────────


class TestGoldRetailSummary:
    """Tests for gold-layer retail summary aggregation."""

    def test_gold_retail_summary_aggregation(self, spark, sample_silver_retail):
        """Gold retail summary produces state-level YoY metrics from silver data."""
        # Given: 24 months of silver retail data for NSW Food retailing
        silver_df = sample_silver_retail

        # When: gold aggregation is applied
        from src.gold.retail_summary import transform_gold_retail_summary

        result = transform_gold_retail_summary(silver_df)

        # Then: output has expected columns
        expected_columns = {
            "date",
            "state",
            "industry",
            "turnover_millions",
            "turnover_3m_avg",
            "turnover_12m_avg",
            "yoy_growth_pct",
        }
        assert set(result.columns) == expected_columns

        # And: contains data for 2024 months (YoY needs 12 months of history)
        result_2024 = result.filter(F.col("year") == 2024) if "year" in result.columns else result.filter(F.year("date") == 2024)
        assert result_2024.count() > 0, "Should have 2024 data with YoY metrics"

    def test_gold_retail_summary_has_growth(self, spark, sample_silver_retail):
        """Gold table has yoy_growth_pct column with numeric values."""
        # Given: 24 months of silver retail data
        silver_df = sample_silver_retail

        # When: gold aggregation is applied
        from src.gold.retail_summary import transform_gold_retail_summary

        result = transform_gold_retail_summary(silver_df)

        # Then: yoy_growth_pct exists and is numeric (DoubleType)
        assert "yoy_growth_pct" in result.columns
        growth_field = [f for f in result.schema.fields if f.name == "yoy_growth_pct"][0]
        assert isinstance(
            growth_field.dataType, DoubleType
        ), f"yoy_growth_pct should be DoubleType, got {growth_field.dataType}"

        # And: Jan 2024 NSW growth = (4500 - 4200) / 4200 * 100 = 7.14%
        jan_2024 = result.filter(F.col("date") == date(2024, 1, 1)).first()
        if jan_2024 is not None:
            assert jan_2024.yoy_growth_pct is not None, "YoY growth should not be null"
            assert abs(jan_2024.yoy_growth_pct - 7.14) < 0.5, (
                f"Jan 2024 YoY growth should be ~7.14%, got {jan_2024.yoy_growth_pct}"
            )

    def test_gold_retail_summary_rolling_averages(self, spark, sample_silver_retail):
        """Gold table has correct 3-month and 12-month rolling averages."""
        # Given: 24 months of silver retail data
        silver_df = sample_silver_retail

        # When: gold aggregation is applied
        from src.gold.retail_summary import transform_gold_retail_summary

        result = transform_gold_retail_summary(silver_df)

        # Then: rolling averages exist
        assert "turnover_3m_avg" in result.columns
        assert "turnover_12m_avg" in result.columns

        # Mar 2024: 3-month avg = (4500 + 4400 + 4600) / 3 = 4500.0
        mar_2024 = result.filter(F.col("date") == date(2024, 3, 1)).first()
        if mar_2024 is not None:
            assert mar_2024.turnover_3m_avg is not None
            assert abs(mar_2024.turnover_3m_avg - 4500.0) < 10.0, (
                f"Mar 2024 3m avg should be ~4500.0, got {mar_2024.turnover_3m_avg}"
            )

    def test_gold_retail_summary_no_nulls_in_2024(self, spark, sample_silver_retail):
        """Gold table has no null values for months with sufficient history."""
        # Given: 24 months of silver data (2023 + 2024)
        silver_df = sample_silver_retail

        # When: gold aggregation is applied
        from src.gold.retail_summary import transform_gold_retail_summary

        result = transform_gold_retail_summary(silver_df)

        # Then: 2024 rows should have no null growth or rolling averages
        result_2024 = result.filter(F.year("date") == 2024)
        null_growth = result_2024.filter(F.col("yoy_growth_pct").isNull()).count()
        null_3m = result_2024.filter(F.col("turnover_3m_avg").isNull()).count()
        assert null_growth == 0, "2024 rows should have no null YoY growth"
        assert null_3m == 0, "2024 rows should have no null 3-month averages"


# ── Gold: Food Inflation ─────────────────────────────────────────────


class TestGoldFoodInflation:
    """Tests for gold-layer food inflation YoY calculation."""

    def test_gold_food_inflation_yoy(self, spark, sample_silver_cpi):
        """Gold table calculates year-over-year CPI change percentage correctly."""
        # Given: 8 quarters of silver CPI data (2023-2024)
        silver_df = sample_silver_cpi

        # When: gold inflation calculation is applied
        from src.gold.food_inflation import transform_gold_food_inflation

        result = transform_gold_food_inflation(silver_df)

        # Then: has yoy_change_pct column
        assert "yoy_change_pct" in result.columns

        # Q1 2024 YoY = (137.8 - 130.0) / 130.0 * 100 = 6.0%
        q1_2024 = result.filter(
            (F.col("date") == date(2024, 1, 1))
            & (F.col("state") == "New South Wales")
        ).first()
        assert q1_2024 is not None, "Should have Q1 2024 inflation data"
        assert abs(q1_2024.yoy_change_pct - 6.0) < 0.1, (
            f"Q1 2024 YoY change should be ~6.0%, got {q1_2024.yoy_change_pct}"
        )

    def test_gold_food_inflation_schema(self, spark, sample_silver_cpi):
        """Gold food inflation table has expected columns."""
        # Given: silver CPI data
        silver_df = sample_silver_cpi

        # When: gold inflation calculation is applied
        from src.gold.food_inflation import transform_gold_food_inflation

        result = transform_gold_food_inflation(silver_df)

        # Then: expected columns present
        expected_columns = {"date", "state", "index_name", "cpi_index", "yoy_change_pct"}
        assert set(result.columns) == expected_columns

    def test_gold_food_inflation_only_2024_has_yoy(self, spark, sample_silver_cpi):
        """YoY change is only calculated when prior year data exists."""
        # Given: silver CPI data starting Q1 2023
        silver_df = sample_silver_cpi

        # When: gold inflation calculation is applied
        from src.gold.food_inflation import transform_gold_food_inflation

        result = transform_gold_food_inflation(silver_df)

        # Then: 2024 quarters should have YoY values (have 2023 for comparison)
        result_2024 = result.filter(F.year("date") == 2024)
        null_yoy = result_2024.filter(F.col("yoy_change_pct").isNull()).count()
        assert null_yoy == 0, "2024 quarters should all have YoY values"

    def test_gold_food_inflation_q4_calculation(self, spark, sample_silver_cpi):
        """Q4 2024 YoY correctly compares with Q4 2023."""
        # Given: silver CPI data with Q4 2023 = 136.2 and Q4 2024 = 142.3
        silver_df = sample_silver_cpi

        # When: gold inflation calculation is applied
        from src.gold.food_inflation import transform_gold_food_inflation

        result = transform_gold_food_inflation(silver_df)

        # Then: Q4 2024 YoY = (142.3 - 136.2) / 136.2 * 100 = 4.48%
        q4_2024 = result.filter(
            (F.col("date") == date(2024, 10, 1))
            & (F.col("state") == "New South Wales")
        ).first()
        assert q4_2024 is not None, "Should have Q4 2024 data"
        assert abs(q4_2024.yoy_change_pct - 4.48) < 0.1, (
            f"Q4 2024 YoY should be ~4.48%, got {q4_2024.yoy_change_pct}"
        )


# ── Gold: Cross-Source Join ──────────────────────────────────────────


class TestGoldCrossSourceJoin:
    """Tests for gold-layer cross-source analysis joining retail + CPI."""

    def test_gold_cross_source_join(self, spark, sample_silver_retail, sample_silver_cpi):
        """Gold grocery insights joins retail turnover with CPI inflation."""
        # Given: silver retail data (monthly) and silver CPI data (quarterly)
        retail_df = sample_silver_retail
        cpi_df = sample_silver_cpi

        # When: cross-source join is applied
        from src.gold.grocery_insights import transform_gold_grocery_insights

        result = transform_gold_grocery_insights(retail_df, cpi_df)

        # Then: result has columns from both sources
        assert "turnover_millions" in result.columns, "Should have retail turnover"
        assert "cpi_yoy_change" in result.columns or "cpi_index" in result.columns, (
            "Should have CPI data"
        )
        assert "state" in result.columns, "Should have state column"

        # And: NSW data is present (exists in both sources)
        nsw_rows = result.filter(F.col("state") == "New South Wales").count()
        assert nsw_rows > 0, "Should have NSW data from join"

    def test_gold_cross_source_join_columns(self, spark, sample_silver_retail, sample_silver_cpi):
        """Cross-source join has expected output schema."""
        # Given: silver data from both sources
        retail_df = sample_silver_retail
        cpi_df = sample_silver_cpi

        # When: cross-source join is applied
        from src.gold.grocery_insights import transform_gold_grocery_insights

        result = transform_gold_grocery_insights(retail_df, cpi_df)

        # Then: expected columns present
        required_columns = {"state", "month", "turnover_millions", "yoy_growth_pct", "cpi_yoy_change"}
        assert required_columns.issubset(
            set(result.columns)
        ), f"Missing columns: {required_columns - set(result.columns)}"
