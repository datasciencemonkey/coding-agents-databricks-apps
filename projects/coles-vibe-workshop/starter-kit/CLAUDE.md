# CLAUDE.md — Grocery Intelligence Platform

## Team
- **Team Name:** TEAM_NAME
- **Schema:** workshop_vibe_coding.TEAM_SCHEMA

Replace `TEAM_NAME` and `TEAM_SCHEMA` above with your assigned values (e.g., `team_01`).

## Project
A data platform that ingests Australian retail and food price data, transforms it through a medallion architecture, and serves analytics via a web app with natural language querying.

## Tech Stack
- **Data processing:** PySpark (never pandas)
- **Pipeline framework:** Lakeflow Declarative Pipelines (`import databricks.declarative_pipelines as dp`)
- **Pipeline decorators:** `@dp.table` for tables, `@dp.materialized_view` for views
- **Data quality:** `@dp.expect("name", "SQL_EXPRESSION")` on pipeline tables
- **Web backend:** FastAPI with Pydantic models
- **Web frontend:** HTML + Tailwind CSS (CDN) + htmx (CDN) — no npm/node required
- **Database access:** `databricks-sql-connector` with parameterized queries only
- **Deployment:** Databricks Asset Bundles (`databricks bundle deploy`)
- **Testing:** pytest with PySpark test fixtures

## Data Standards
- **Catalog:** `workshop_vibe_coding`
- **Schema:** `TEAM_SCHEMA`
- **Architecture:** Bronze (raw) → Silver (cleaned/decoded) → Gold (aggregated)
- **Date columns:** `YYYY-MM-DD` format, stored as DATE type
- **Naming:** snake_case for all table and column names

## Rules
- Always use PySpark, never pandas
- Always use parameterized SQL queries — never string concatenation
- Write tests BEFORE implementation
- Use small test DataFrames (5-10 rows) in pytest fixtures — don't mock the database
- Keep solutions minimal — don't over-engineer
- Don't change functions that are already passing tests
- One function per file in the pipeline (bronze, silver, gold layers)

## Project Structure
```
├── CLAUDE.md
├── databricks.yml
├── src/
│   ├── bronze/
│   │   ├── abs_retail_trade.py
│   │   └── abs_cpi_food.py
│   ├── silver/
│   │   ├── retail_turnover.py
│   │   └── food_price_index.py
│   └── gold/
│       ├── retail_summary.py
│       └── food_inflation.py
├── tests/
│   ├── conftest.py
│   ├── test_pipeline.py
│   └── test_app.py
└── app/
    ├── app.py
    ├── app.yaml
    ├── requirements.txt
    └── static/
        └── index.html
```

## Data Sources
| Source | API | Format |
|--------|-----|--------|
| ABS Retail Trade | `https://data.api.abs.gov.au/data/ABS,RT,1.0.0/...` | CSV (SDMX) |
| ABS Consumer Price Index | `https://data.api.abs.gov.au/data/ABS,CPI,2.0.0/...` | CSV (SDMX) |

## Code Mappings (for silver layer)
**Regions:** 1=New South Wales, 2=Victoria, 3=Queensland, 4=South Australia, 5=Western Australia, 6=Tasmania, 7=Northern Territory, 8=Australian Capital Territory

**Industries:** 20=Food retailing, 41=Clothing/footwear/personal, 42=Department stores, 43=Other retailing, 44=Cafes/restaurants/takeaway, 45=Household goods retailing

**CPI Index:** 10001=All groups CPI, 20001=Food and non-alcoholic beverages
