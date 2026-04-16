## Track: Data Engineering

### Pipeline Framework
- Use Lakeflow Declarative Pipelines: `import databricks.declarative_pipelines as dp`
- `@dp.table` for streaming/batch tables
- `@dp.materialized_view` for aggregation views
- Data quality: `@dp.expect("name", "SQL_EXPRESSION")`, `@dp.expect_or_fail()`, `@dp.expect_all()`

### Pipeline File Structure
- One function per file in src/bronze/, src/silver/, src/gold/
- Each file is a notebook that Lakeflow runs independently
- Bronze reads from APIs/files, Silver decodes/cleans, Gold aggregates

### Deployment
- Databricks Asset Bundles: `databricks.yml` + `resources/pipeline.yml`
- Always validate before deploying: `databricks bundle validate`
- Target: serverless Lakeflow pipeline

### Data Sources
- ABS Retail Trade API: `https://data.api.abs.gov.au/data/ABS,RT,1.0.0/...`
- ABS CPI Food API: `https://data.api.abs.gov.au/data/ABS,CPI,2.0.0/...`
- Both return CSV via SDMX format with `spark.read.csv(url, header=True, inferSchema=True)`
