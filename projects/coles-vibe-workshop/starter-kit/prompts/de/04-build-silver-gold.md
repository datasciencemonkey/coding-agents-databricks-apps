## Step 4: Build Silver + Gold Layers

Silver = cleaned and decoded. Gold = aggregated and analytics-ready.

### Prompt

Paste this into Claude Code:

```
Build the silver and gold layers to make all remaining tests pass.

SILVER LAYER:

1. src/silver/retail_turnover.py
   - @dp.table that reads from the bronze retail trade table
   - Decode REGION codes: 1=New South Wales, 2=Victoria, 3=Queensland, 4=South Australia, 5=Western Australia, 6=Tasmania, 7=Northern Territory, 8=Australian Capital Territory
   - Decode INDUSTRY codes: 20=Food retailing, 41=Clothing/footwear/personal, 42=Department stores, 43=Other retailing, 44=Cafes/restaurants/takeaway, 45=Household goods retailing
   - Parse TIME_PERIOD "2024-01" to a proper date column
   - Rename OBS_VALUE to turnover_millions

2. src/silver/food_price_index.py
   - @dp.table that reads from the bronze CPI table
   - Decode REGION codes (same as above)
   - Decode INDEX codes: 10001=All groups CPI, 20001=Food and non-alcoholic beverages
   - Rename OBS_VALUE to cpi_index

GOLD LAYER:

3. src/gold/retail_summary.py
   - @dp.materialized_view reading from silver retail_turnover
   - Add turnover_3m_avg: 3-month rolling average per state/industry
   - Add turnover_12m_avg: 12-month rolling average per state/industry
   - Add yoy_growth_pct: year-over-year growth percentage

4. src/gold/food_inflation.py
   - @dp.materialized_view reading from silver food_price_index
   - Add yoy_change_pct: year-over-year CPI change percentage

Run ALL tests: pytest tests/test_pipeline.py -x
Fix any failures until everything is green.
```

### Expected Result

Four new files in `src/silver/` and `src/gold/`. All 10 pipeline tests pass.

### If It Doesn't Work

- **Agent uses pandas:** Say "Use PySpark window functions, not pandas. Check CLAUDE.md."
- **Rolling averages wrong:** Ensure the window is ordered by date and partitioned by state + industry.
- **Running out of time:** Grab Checkpoint 1B — pre-loaded silver and gold tables in your schema.
  ```
  Copy checkpoint tables to our schema. Run:
  CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.retail_summary AS SELECT * FROM workshop_vibe_coding.checkpoints.retail_summary;
  CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy AS SELECT * FROM workshop_vibe_coding.checkpoints.food_inflation_yoy;
  ```
