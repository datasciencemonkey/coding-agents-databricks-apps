## Step 2: Write Pipeline Tests

Tests are your spec. Write them BEFORE any implementation.

### Prompt

Paste this into Claude Code:

```
Create pytest tests for a Lakeflow Declarative Pipeline in tests/test_pipeline.py.
Use the fixtures from tests/conftest.py (spark, sample_retail_csv, sample_cpi_csv).

Write these tests:

1. test_bronze_retail_trade_schema:
   - Raw CSV data has all original columns: DATAFLOW, FREQ, MEASURE, INDUSTRY, REGION, TIME_PERIOD, OBS_VALUE
   - Test: given sample_retail_csv, assert correct columns exist

2. test_bronze_retail_trade_not_null:
   - TIME_PERIOD and OBS_VALUE are never null
   - Test: assert no nulls in these columns

3. test_silver_retail_turnover_decodes_regions:
   - REGION codes decoded to state names (1=New South Wales, 2=Victoria, 3=Queensland, 4=South Australia, 5=Western Australia, 6=Tasmania, 7=Northern Territory, 8=Australian Capital Territory)
   - Test: given bronze rows with code "1", silver rows have "New South Wales"

4. test_silver_retail_turnover_decodes_industries:
   - INDUSTRY codes decoded (20=Food retailing, 41=Clothing/footwear/personal, 42=Department stores, 43=Other retailing, 44=Cafes/restaurants/takeaway, 45=Household goods retailing)
   - Test: given bronze rows with code "20", silver rows have "Food retailing"

5. test_silver_retail_turnover_parses_dates:
   - TIME_PERIOD string "2024-01" parsed to proper date column
   - Test: assert date type and correct value

6. test_gold_retail_summary_rolling_averages:
   - Adds 3-month and 12-month rolling averages
   - Test: given 24 months of silver data, verify rolling averages are correct

7. test_gold_retail_summary_yoy_growth:
   - Adds year-over-year growth percentage
   - Test: given 24 months of data, verify YoY growth = (current - same_month_last_year) / same_month_last_year * 100

8. test_bronze_cpi_schema:
   - CPI data has columns: DATAFLOW, FREQ, MEASURE, INDEX, REGION, TIME_PERIOD, OBS_VALUE

9. test_silver_food_price_index_decodes:
   - INDEX codes decoded (10001=All groups CPI, 20001=Food and non-alcoholic beverages)
   - REGION codes decoded to state names

10. test_gold_food_inflation_yoy:
    - Calculates year-over-year CPI change percentage
    - Test: given 8 quarters of data, verify YoY change is correct

Write ONLY the tests. Do NOT implement any pipeline functions yet.
Use PySpark test fixtures with small DataFrames (5-10 rows each).
Import transformation functions from src/ modules (they don't exist yet — that's fine).
```

### Expected Result

A `tests/test_pipeline.py` file with 10 test functions. All tests should FAIL when you run them (because the implementation doesn't exist yet). That's correct — this is TDD.

### If It Doesn't Work

- **Agent writes implementation too:** Say "Stop. Delete the implementation. I only want the tests."
- **Agent uses pandas:** Say "Use PySpark, not pandas. Check CLAUDE.md."
- **Import errors:** That's expected — the src/ modules don't exist yet.
