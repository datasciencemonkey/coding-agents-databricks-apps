"""
Pipeline test stubs for Lab 1.
These define WHAT the pipeline should do. The agent implements the code to make them pass.
Copy to tests/test_pipeline.py before starting Lab 1.
"""


# ── Bronze: Retail Trade ──────────────────────────────────────────────


def test_bronze_retail_trade_schema(spark, sample_retail_csv):
    """Bronze retail table has all expected columns from the API."""
    expected_columns = {"DATAFLOW", "FREQ", "MEASURE", "INDUSTRY", "REGION", "TIME_PERIOD", "OBS_VALUE"}
    # TODO: Pass sample_retail_csv through bronze ingestion
    # TODO: Assert output columns match expected_columns
    pass


def test_bronze_retail_trade_not_null(spark, sample_retail_csv):
    """TIME_PERIOD and OBS_VALUE are never null in bronze table."""
    # TODO: Pass sample_retail_csv through bronze ingestion
    # TODO: Assert no nulls in TIME_PERIOD column
    # TODO: Assert no nulls in OBS_VALUE column
    pass


# ── Silver: Retail Turnover ───────────────────────────────────────────


def test_silver_retail_turnover_decodes_regions(spark, sample_retail_csv):
    """REGION code '1' becomes 'New South Wales', '2' becomes 'Victoria', etc."""
    # TODO: Pass bronze data through silver transformation
    # TODO: Assert REGION "1" is decoded to "New South Wales"
    # TODO: Assert REGION "2" is decoded to "Victoria"
    # TODO: Assert REGION "3" is decoded to "Queensland"
    pass


def test_silver_retail_turnover_decodes_industries(spark, sample_retail_csv):
    """INDUSTRY code '20' becomes 'Food retailing', '41' becomes 'Clothing/footwear/personal'."""
    # TODO: Pass bronze data through silver transformation
    # TODO: Assert INDUSTRY "20" is decoded to "Food retailing"
    # TODO: Assert INDUSTRY "41" is decoded to "Clothing/footwear/personal"
    pass


def test_silver_retail_turnover_parses_dates(spark, sample_retail_csv):
    """TIME_PERIOD string '2024-01' is parsed to a proper date column."""
    # TODO: Pass bronze data through silver transformation
    # TODO: Assert TIME_PERIOD is converted to DateType
    # TODO: Assert "2024-01" becomes date(2024, 1, 1)
    pass


# ── Gold: Retail Summary ─────────────────────────────────────────────


def test_gold_retail_summary_rolling_averages(spark):
    """Gold table has 3-month and 12-month rolling averages."""
    # TODO: Create 24 months of silver-like data for one state/industry
    # TODO: Pass through gold transformation
    # TODO: Assert turnover_3m_avg is average of last 3 months
    # TODO: Assert turnover_12m_avg is average of last 12 months
    pass


def test_gold_retail_summary_yoy_growth(spark):
    """Gold table has year-over-year growth percentage."""
    # TODO: Create 24 months of silver-like data
    # TODO: Pass through gold transformation
    # TODO: Assert yoy_growth_pct = (current - same_month_last_year) / same_month_last_year * 100
    pass


# ── Bronze: CPI Food ─────────────────────────────────────────────────


def test_bronze_cpi_schema(spark, sample_cpi_csv):
    """Bronze CPI table has all expected columns."""
    expected_columns = {"DATAFLOW", "FREQ", "MEASURE", "INDEX", "REGION", "TIME_PERIOD", "OBS_VALUE"}
    # TODO: Pass sample_cpi_csv through bronze ingestion
    # TODO: Assert output columns match expected_columns
    pass


# ── Silver: Food Price Index ─────────────────────────────────────────


def test_silver_food_price_index_decodes(spark, sample_cpi_csv):
    """INDEX code '10001' becomes 'All groups CPI', '20001' becomes 'Food and non-alcoholic beverages'."""
    # TODO: Pass bronze CPI data through silver transformation
    # TODO: Assert INDEX "10001" decoded to "All groups CPI"
    # TODO: Assert INDEX "20001" decoded to "Food and non-alcoholic beverages"
    # TODO: Assert REGION codes decoded to state names
    pass


# ── Gold: Food Inflation ─────────────────────────────────────────────


def test_gold_food_inflation_yoy(spark):
    """Gold table has year-over-year CPI change percentage."""
    # TODO: Create 8 quarters of silver-like CPI data
    # TODO: Pass through gold transformation
    # TODO: Assert yoy_change_pct = (current_quarter - same_quarter_last_year) / same_quarter_last_year * 100
    pass
