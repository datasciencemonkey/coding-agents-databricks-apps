# CLAUDE.md — Grocery Intelligence Demo Pipeline

## Project

Demo pipeline for the Coles Vibe Coding Workshop opening. Ingests Australian retail and food price data from the ABS, transforms through bronze/silver/gold, and serves analytics-ready tables for the demo app.

This is the **facilitator's pre-built pipeline** — deployed before the workshop so gold tables are ready for the opening demo. Teams build their own version during Lab 1.

## Tech Stack

- **Pipeline framework:** Lakeflow Declarative Pipelines (`import dlt` with `databricks.declarative_pipelines` fallback)
- **Data processing:** PySpark (never pandas)
- **Data quality:** `@dp.expect()`, `@dp.expect_or_fail()`
- **Deployment:** Databricks Asset Bundles with `DATABRICKS_BUNDLE_ENGINE=direct`
- **Testing:** Python Behave (BDD) with Gherkin feature files

## Data Standards

- **Catalog:** `workshop_vibe_coding`
- **Schema:** `demo`
- **Architecture:** Bronze (raw from UC volumes) → Silver (decoded, typed) → Gold (aggregated)
- **Column naming:** snake_case
- **Date columns:** DATE type
- **Nulls:** Bronze may contain nulls; Silver filters them; Gold has zero nulls

## Data Sources

| Source | Location | Format | What It Contains |
|--------|----------|--------|-----------------|
| ABS Retail Trade | `/Volumes/workshop_vibe_coding/demo/raw_data/abs_retail_trade.csv` | CSV | Monthly retail turnover by state & industry since 2010 |
| ABS CPI | `/Volumes/workshop_vibe_coding/demo/raw_data/abs_cpi_food.csv` | CSV | Quarterly CPI indices by state since 2010 |

## Code Mappings

### Region Codes (INT)

| Code | State |
|------|-------|
| 1 | New South Wales |
| 2 | Victoria |
| 3 | Queensland |
| 4 | South Australia |
| 5 | Western Australia |
| 6 | Tasmania |
| 7 | Northern Territory |
| 8 | Australian Capital Territory |

### Industry Codes (INT, Retail Trade only)

| Code | Industry |
|------|----------|
| 20 | Food retailing |
| 41 | Clothing, footwear and personal accessories |
| 42 | Department stores |
| 43 | Other retailing |
| 44 | Cafes, restaurants and takeaway |
| 45 | Household goods retailing |

## Tables

| Table | Layer | Rows | Description |
|-------|-------|------|-------------|
| `bronze_abs_retail_trade` | Bronze | ~8,900 | Raw ABS retail data |
| `bronze_abs_cpi_food` | Bronze | ~500 | Raw ABS CPI data |
| `silver_retail_turnover` | Silver | ~8,200 | Decoded states, industries, dates |
| `silver_food_price_index` | Silver | ~500 | Decoded states, quarterly CPI |
| `gold_retail_summary` | Gold | ~1,500 | Monthly turnover + 3m/12m avg + YoY growth |
| `gold_food_inflation_yoy` | Gold | ~480 | Quarterly CPI inflation by state |

## Rules

- PySpark only, never pandas
- Use `@dp.expect` / `@dp.expect_or_fail` for data quality
- One transformation per file
- Import dlt with fallback: `try: import databricks.declarative_pipelines as dp / except: import dlt as dp`
- Read raw data from UC volumes, not external APIs (serverless compute blocks external HTTPS)

## Commands

```bash
# Validate
DATABRICKS_BUNDLE_ENGINE=direct databricks bundle validate

# Deploy
DATABRICKS_BUNDLE_ENGINE=direct databricks bundle deploy

# Run pipeline
DATABRICKS_BUNDLE_ENGINE=direct databricks bundle run grocery_pipeline

# Run BDD tests
uv run behave
```
