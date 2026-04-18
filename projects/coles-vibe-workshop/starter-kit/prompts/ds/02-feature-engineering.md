## Step 2: Build Feature Engineering Pipeline

Write tests first, then build the features.

### Prompt

```
Create a feature engineering pipeline that reads from our gold tables and produces a feature table.

Write tests first in tests/test_features.py, then implement:

1. Lag features from retail_summary:
   - turnover_lag_1m, turnover_lag_3m, turnover_lag_6m, turnover_lag_12m
   - Use PySpark Window functions partitioned by state + industry, ordered by month

2. Seasonal features:
   - month_of_year (1-12), quarter (1-4), is_december (boolean), is_q4 (boolean)
   - Extract from the month date column

3. Growth rate features:
   - turnover_mom_growth: month-over-month growth percentage
   - turnover_yoy_growth: year-over-year growth percentage (use lag_12m)
   - cpi_yoy_change: join with food_inflation_yoy on state + quarter

4. Write the combined feature table to:
   workshop_vibe_coding.TEAM_SCHEMA.retail_features

Run tests after implementation. Handle nulls in lag features (first N rows will be null — that's expected, filter them out in the final table).
```

### Expected Result

A feature table in Unity Catalog with lag, seasonal, and growth columns. All tests pass.

### If It Doesn't Work

- **Window function errors:** Verify `orderBy("month")` and `partitionBy("state", "industry")`
- **Agent uses pandas:** Say "Use PySpark Window functions. Check CLAUDE.md."
- **Null lag values:** Expected for first N rows. Use `.filter(col("turnover_lag_12m").isNotNull())`
