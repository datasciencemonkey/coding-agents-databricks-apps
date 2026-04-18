## Step 6: Add Data Quality Rules

### Prompt

```
Add comprehensive data quality expectations across all pipeline tables:

Bronze tables:
- @dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
- @dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")
- @dp.expect("valid_date_range", "TIME_PERIOD >= '2010-01'")

Silver tables:
- @dp.expect_or_fail("valid_state", "state IN ('New South Wales','Victoria','Queensland','South Australia','Western Australia','Tasmania','Northern Territory','Australian Capital Territory')")
- @dp.expect("valid_turnover", "turnover_millions > 0")
- @dp.expect("no_unknown_industry", "industry != 'Unknown'")

Gold tables:
- @dp.expect("valid_yoy", "yoy_growth_pct BETWEEN -100 AND 500")
- @dp.expect("valid_rolling_avg", "turnover_3m_avg > 0")

Also create a gold-level cross-source view:
- src/gold/grocery_insights.py: @dp.materialized_view
- Joins retail_summary + food_inflation_yoy + food_recalls (if available)
- Columns: state, month, turnover_millions, yoy_growth_pct, cpi_yoy_change, recall_count

Run all tests to verify nothing breaks.
```

### Expected Result

All existing tables have data quality expectations. A new cross-source gold view is created.

### If It Doesn't Work

- **@dp.expect_or_fail stops pipeline:** Start with `@dp.expect` (warn only), then upgrade after verifying data
- **Cross-source join duplicates:** Join on state + date range, not exact date (CPI is quarterly, retail is monthly)
