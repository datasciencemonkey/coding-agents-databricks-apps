## Step 1: Explore Gold Tables

Understand the data you'll be building features from.

### Prompt

```
Query these tables and show me a comprehensive analysis:

1. workshop_vibe_coding.TEAM_SCHEMA.retail_summary:
   - Row count, date range, distinct states, distinct industries
   - Summary statistics for turnover_millions (min, max, mean, stddev)
   - Top 5 state-industry combinations by average turnover
   - Any null values or data quality issues

2. workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy:
   - Row count, date range, distinct states
   - Summary statistics for yoy_change_pct
   - States with highest and lowest inflation

Show me the results as tables.
```

### Expected Result

Summary tables showing data distributions, ranges, and any quality issues.

### If It Doesn't Work

- **Table not found:** Check schema name. Try `workshop_vibe_coding.checkpoints.retail_summary` instead.
- **Permission error:** Run `databricks auth status` to verify your token.
