# Grocery Intelligence Platform — Reference Implementation

Reference implementation for the Coles Vibe Coding Workshop. This is the
"gold standard" solution that participants work towards during the hackathon.

Built following Anthropic best practices: **CLAUDE.md -> Tests -> Implementation**.

## File Structure

```
reference-implementation/
├── databricks.yml              # DABs bundle config (includes resources/)
├── resources/
│   └── pipeline.yml            # Lakeflow pipeline + daily job definitions
├── src/
│   ├── bronze/                 # Raw ingestion (ABS retail, ABS CPI, FSANZ recalls)
│   ├── silver/                 # Cleaned & decoded tables
│   └── gold/                   # Aggregated analytics tables
├── tests/                      # pytest suite (PySpark fixtures, no mocks)
├── app/
│   ├── app.py                  # FastAPI application
│   ├── app.yaml                # Databricks Apps config
│   ├── requirements.txt        # Python dependencies
│   └── static/
│       └── index.html          # Single-page dashboard (Tailwind + htmx)
└── README.md
```

## Run Tests

```bash
cd reference-implementation
pytest tests/ -x
```

## Deploy

```bash
# Validate the bundle configuration
databricks bundle validate -t dev

# Deploy pipeline, job, and app
databricks bundle deploy -t dev
```

## App Endpoints

| Method | Path           | Description                              |
|--------|----------------|------------------------------------------|
| GET    | `/health`      | Health check                             |
| GET    | `/`            | Dashboard UI                             |
| GET    | `/api/metrics` | KPIs: top states, trend, YoY, inflation  |
| GET    | `/api/recalls` | Recent food recalls                      |
| POST   | `/api/ask`     | Natural language query (Foundation Model) |

## Environment Variables

The app expects these environment variables (set automatically by Databricks Apps):

- `DATABRICKS_HOST` — Workspace hostname
- `DATABRICKS_TOKEN` — PAT or OAuth token
- `SQL_WAREHOUSE_ID` — SQL warehouse for queries
- `CATALOG` — Unity Catalog name (default: `workshop_vibe_coding`)
- `SCHEMA` — Schema name (default: `reference`)
