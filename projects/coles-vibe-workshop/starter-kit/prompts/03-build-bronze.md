## Step 3: Build Bronze Layer

Bronze = raw data ingestion. No transformations, just get the data in.

### Prompt

Paste this into Claude Code:

```
Create the bronze layer for our Lakeflow Declarative Pipeline:

1. src/bronze/abs_retail_trade.py
   - Use @dp.table decorator (import databricks.declarative_pipelines as dp)
   - Ingest ABS Retail Trade API CSV: https://data.api.abs.gov.au/data/ABS,RT,1.0.0/M1.20+41+42+43+44+45.20.1+2+3+4+5+6+7+8.M?format=csv&startPeriod=2010-01
   - Use spark.read.csv() with header=True and inferSchema=True
   - Add data quality expectations:
     @dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
     @dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")

2. src/bronze/abs_cpi_food.py
   - Same pattern with @dp.table
   - Ingest ABS CPI Food API CSV: https://data.api.abs.gov.au/data/ABS,CPI,2.0.0/1.10001+20001.10.1+2+3+4+5+6+7+8.Q?format=csv&startPeriod=2010-Q1
   - Same data quality expectations

Unity Catalog target: workshop_vibe_coding.TEAM_SCHEMA

Then run the bronze tests: pytest tests/test_pipeline.py -k "bronze" -x
Fix any failures.
```

### Expected Result

Two files in `src/bronze/`, each with a `@dp.table` decorated function. Bronze tests should pass.

### If It Doesn't Work

- **API timeout:** The ABS APIs can be slow from some networks. Try once more.
- **Still failing:** Use checkpoint data instead. Tell the agent:
  ```
  The API is not accessible. Instead, read from the checkpoint tables:
  - spark.read.table("workshop_vibe_coding.checkpoints.abs_retail_trade_bronze")
  - spark.read.table("workshop_vibe_coding.checkpoints.abs_cpi_food_bronze")
  ```
- **@dp.table not found:** Make sure the import is `import databricks.declarative_pipelines as dp`, not `import dlt`.
