# Grocery Intelligence Demo Pipeline

Pre-built Lakeflow SDP pipeline for the Coles Vibe Coding Workshop opening demo. Ingests Australian Bureau of Statistics retail trade and CPI data through a medallion architecture.

## Tables

| Table | Layer | Description |
|-------|-------|-------------|
| `bronze_abs_retail_trade` | Bronze | Raw ABS monthly retail turnover |
| `bronze_abs_cpi_food` | Bronze | Raw ABS quarterly CPI indices |
| `silver_retail_turnover` | Silver | Decoded states, industries, parsed dates |
| `silver_food_price_index` | Silver | Decoded states, quarterly CPI |
| `gold_retail_summary` | Gold | Monthly turnover + rolling avg + YoY growth |
| `gold_food_inflation_yoy` | Gold | Quarterly inflation rate by state |

## Quick start

```bash
make deploy    # validate + deploy to Databricks
make run       # trigger pipeline refresh
make test      # BDD tests against deployed tables
```

## Project structure

```
demo-pipeline/
├── CLAUDE.md                  # Agent instructions
├── databricks.yml             # Bundle config
├── Makefile                   # Command interface
├── pyproject.toml             # Python config + test deps
├── resources/
│   └── pipeline.yml           # Pipeline + job definitions
├── src/
│   ├── bronze/                # Raw ingestion from UC volumes
│   ├── silver/                # Decode, type, clean
│   └── gold/                  # Aggregate, rolling avg, YoY
└── features/
    ├── environment.py         # Behave hooks (workspace connection)
    ├── pipeline.feature       # 9 Gherkin scenarios
    └── steps/
        └── pipeline_steps.py  # Step definitions
```
