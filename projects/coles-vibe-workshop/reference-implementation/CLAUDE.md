# CLAUDE.md — Grocery Intelligence Platform (Reference Implementation)

## Team
- **Team Name:** reference
- **Schema:** workshop_vibe_coding.reference

## Project
A production-grade data platform that ingests Australian retail and food price data from the ABS, transforms it through a medallion architecture (Bronze/Silver/Gold), and serves analytics via a FastAPI + htmx web app with natural language querying. This is the gold-standard reference implementation demonstrating Anthropic best practices: specs first, then tests, then code.

## Tech Stack
- **Data processing:** PySpark (never pandas)
- **Pipeline framework:** Lakeflow Declarative Pipelines (`import databricks.declarative_pipelines as dp`)
- **Pipeline decorators:** `@dp.table` for streaming/batch tables, `@dp.materialized_view` for aggregation views
- **Data quality:** `@dp.expect("name", "SQL_EXPRESSION")`, `@dp.expect_or_fail()`, `@dp.expect_all()`
- **Web backend:** FastAPI with Pydantic models
- **Web frontend:** HTML + Tailwind CSS (CDN) + htmx (CDN) — no npm/node required
- **Database access:** `databricks-sql-connector` with parameterized queries only
- **Deployment:** Databricks Asset Bundles (`databricks bundle deploy`)
- **Testing:** pytest with PySpark test fixtures

## Data Standards
- **Catalog:** `workshop_vibe_coding`
- **Schema:** `reference`
- **Architecture:** Bronze (raw ingestion) -> Silver (cleaned, decoded, typed) -> Gold (aggregated, analytics-ready)
- **Column naming:** snake_case for all table and column names
- **Date columns:** stored as DATE type (not string, not timestamp)
- **Currency/numeric columns:** DECIMAL(15,2) for monetary values, DOUBLE for indices
- **Nulls:** Bronze may contain nulls; Silver must filter or reject nulls; Gold must have zero nulls

## Rules
- **TDD always:** Write tests BEFORE implementation. Tests are the spec.
- **PySpark not pandas:** Always use PySpark for data processing. Never use pandas.
- **Parameterized queries only:** Never use string concatenation for SQL. Use parameterized queries.
- **Minimal solutions:** Don't over-engineer. Write the simplest code that makes the tests pass.
- **Don't change passing tests:** Never modify a function that already has passing tests unless explicitly asked.
- **One function per file:** Each bronze/silver/gold transformation lives in its own file.
- **Given-When-Then:** Structure all tests with Given (setup), When (action), Then (assertions).
- **Small test DataFrames:** Use 5-10 rows per fixture. Don't mock the database.

## Project Structure
```
reference-implementation/
├── CLAUDE.md                          # This file — project spec and rules
├── databricks.yml                     # DABs deployment config
├── resources/
│   └── pipeline.yml                   # Lakeflow pipeline definition
├── src/
│   ├── bronze/
│   │   ├── abs_retail_trade.py        # Ingest ABS Retail Trade API -> bronze
│   │   ├── abs_cpi_food.py            # Ingest ABS CPI Food API -> bronze
│   │   └── fsanz_food_recalls.py      # Ingest FSANZ food recalls -> bronze
│   ├── silver/
│   │   ├── retail_turnover.py         # Decode regions/industries, parse dates
│   │   ├── food_price_index.py        # Decode indices/regions, rename columns
│   │   └── food_recalls.py            # Clean dates, normalize states
│   └── gold/
│       ├── retail_summary.py          # Rolling averages, YoY growth
│       ├── food_inflation.py          # YoY CPI change percentage
│       └── grocery_insights.py        # Cross-source join: retail + CPI + recalls
├── tests/
│   ├── conftest.py                    # PySpark fixtures, sample DataFrames
│   ├── test_pipeline.py              # Bronze/Silver/Gold transformation tests
│   ├── test_app.py                    # FastAPI endpoint tests
│   └── test_quality.py               # Data quality expectation tests
└── app/
    ├── app.py                         # FastAPI backend
    ├── app.yaml                       # Databricks Apps config
    ├── requirements.txt               # Python dependencies
    └── static/
        └── index.html                 # htmx + Tailwind frontend
```

## Data Sources

| Source | API Endpoint | Format | Frequency | What It Contains |
|--------|-------------|--------|-----------|-----------------|
| **ABS Retail Trade** | `https://data.api.abs.gov.au/data/ABS,RT,1.0.0/M1.20+41+42+43+44+45.20.1+2+3+4+5+6+7+8.M?format=csv` | CSV (SDMX) | Monthly | Retail turnover by state & industry since 2010 |
| **ABS Consumer Price Index** | `https://data.api.abs.gov.au/data/ABS,CPI,2.0.0/1.10001+20001.10.1+2+3+4+5+6+7+8.Q?format=csv` | CSV (SDMX) | Quarterly | Food price indices by state since 2010 |
| **FSANZ Food Recalls** | `https://www.foodstandards.gov.au/food-recalls/recalls` | HTML/RSS | Ad-hoc | Australian food recall notices |

### ABS SDMX API Notes
- Add `&startPeriod=YYYY-MM&endPeriod=YYYY-MM` to filter date ranges
- Retail Trade uses monthly periods (`2024-01`), CPI uses quarterly (`2024-Q1`)
- Both return CSV with headers when `format=csv` is specified
- Rate-limited; cache responses where possible

## Code Mappings (Silver Layer)

### Region Codes (ABS REGION field)
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

### Industry Codes (ABS INDUSTRY field — Retail Trade)
| Code | Industry |
|------|----------|
| 20 | Food retailing |
| 41 | Clothing, footwear and personal accessory retailing |
| 42 | Department stores |
| 43 | Other retailing |
| 44 | Cafes, restaurants and takeaway food services |
| 45 | Household goods retailing |

### CPI Index Codes (ABS INDEX field — Consumer Price Index)
| Code | Index |
|------|-------|
| 10001 | All groups CPI |
| 20001 | Food and non-alcoholic beverages |

## Table Schemas

### Bronze Tables (raw ingestion, original column names preserved)

**bronze_retail_trade:**
`DATAFLOW (STRING), FREQ (STRING), MEASURE (STRING), INDUSTRY (STRING), REGION (STRING), TIME_PERIOD (STRING), OBS_VALUE (DOUBLE), _ingested_at (TIMESTAMP)`

**bronze_cpi_food:**
`DATAFLOW (STRING), FREQ (STRING), MEASURE (STRING), INDEX (STRING), REGION (STRING), TIME_PERIOD (STRING), OBS_VALUE (DOUBLE), _ingested_at (TIMESTAMP)`

**bronze_food_recalls:**
`product (STRING), category (STRING), issue (STRING), date (STRING), state (STRING), url (STRING), _ingested_at (TIMESTAMP)`

### Silver Tables (cleaned, decoded, typed)

**silver_retail_turnover:**
`date (DATE), state (STRING), industry (STRING), turnover_millions (DECIMAL(15,2)), month (INT), year (INT), quarter (INT)`

**silver_food_price_index:**
`date (DATE), state (STRING), index_name (STRING), cpi_index (DOUBLE), quarter (INT), year (INT)`

**silver_food_recalls:**
`date (DATE), state (STRING), product (STRING), category (STRING), issue (STRING), url (STRING)`

### Gold Tables (aggregated, analytics-ready)

**gold_retail_summary:**
`date (DATE), state (STRING), industry (STRING), turnover_millions (DECIMAL(15,2)), turnover_3m_avg (DECIMAL(15,2)), turnover_12m_avg (DECIMAL(15,2)), yoy_growth_pct (DOUBLE)`

**gold_food_inflation:**
`date (DATE), state (STRING), index_name (STRING), cpi_index (DOUBLE), yoy_change_pct (DOUBLE)`

**gold_grocery_insights:**
`state (STRING), month (DATE), turnover_millions (DECIMAL(15,2)), yoy_growth_pct (DOUBLE), cpi_yoy_change (DOUBLE), recall_count (INT)`
