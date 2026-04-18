# Cheatsheet — Quick Fixes

## Common Problems

| Problem | Fix |
|---------|-----|
| **Agent uses pandas** | Add to CLAUDE.md: `Always use PySpark, never pandas`. Then tell the agent: "Rewrite this using PySpark." |
| **SparkSession errors in tests** | Check `tests/conftest.py` has `SparkSession.builder.master("local[*]")` |
| **ABS API timeout or network error** | Use checkpoint tables instead. Tell the agent: `Read from workshop_vibe_coding.checkpoints.<table_name> instead of calling the API` |
| **`@dp.table` not found** | Use `import databricks.declarative_pipelines as dp`, NOT `import dlt` |
| **CORS errors in browser** | Add to `app.py`: `app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])` |
| **Agent rewrites working code** | Say: "Don't change functions that already pass tests. Only fix the failing ones." |
| **Can't write to Unity Catalog** | Check your schema name: `workshop_vibe_coding.team_XX`. Run `databricks auth status` to verify access. |
| **htmx not loading** | Add to `<head>`: `<script src="https://unpkg.com/htmx.org@2.0.4"></script>` |
| **databricks-sql-connector errors** | Run `pip install databricks-sql-connector`. Check env vars: `echo $DATABRICKS_HOST` |
| **Pipeline deploy fails** | Run `databricks bundle validate` first. Check `databricks.yml` syntax. |
| **Agent goes off track** | Say "stop" then give a specific instruction. Don't let it keep going. |
| **Agent generates too much code** | Say "Keep it minimal. Just make the failing test pass." |
| **Running out of time** | Grab the next checkpoint. No shame — the goal is to have a working demo! |

## Useful Commands

```bash
# Check your Databricks connection
databricks auth status

# Run specific tests
pytest tests/test_pipeline.py -k "bronze" -x
pytest tests/test_pipeline.py -k "silver" -x
pytest tests/test_pipeline.py -k "gold" -x
pytest tests/test_app.py -x

# Run all tests
pytest tests/ -x

# Validate DABs bundle
databricks bundle validate

# Deploy pipeline
databricks bundle deploy -t dev
databricks bundle run grocery-intelligence-TEAM_NAME -t dev

# Deploy app
cd app && databricks apps deploy --name grocery-app-TEAM_NAME --source-code-path ./

# Start app locally for testing
cd app && uvicorn app:app --reload --port 8000
```

## Checkpoint Recovery

If you're stuck and need to catch up:

```sql
-- Checkpoint 1A: Bronze tables
CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.abs_retail_trade_bronze
  AS SELECT * FROM workshop_vibe_coding.checkpoints.abs_retail_trade_bronze;

CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.abs_cpi_food_bronze
  AS SELECT * FROM workshop_vibe_coding.checkpoints.abs_cpi_food_bronze;

-- Checkpoint 1B: Silver + Gold tables
CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.retail_turnover
  AS SELECT * FROM workshop_vibe_coding.checkpoints.retail_turnover;

CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.food_price_index
  AS SELECT * FROM workshop_vibe_coding.checkpoints.food_price_index;

CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.retail_summary
  AS SELECT * FROM workshop_vibe_coding.checkpoints.retail_summary;

CREATE TABLE workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy
  AS SELECT * FROM workshop_vibe_coding.checkpoints.food_inflation_yoy;
```

## Data Science Track

| Problem | Fix |
|---------|-----|
| **MLflow tracking URI error** | Check `DATABRICKS_HOST` env var: `echo $DATABRICKS_HOST` |
| **MLflow experiment not found** | Set explicitly: `mlflow.set_experiment("/Users/.../name")` |
| **Feature table write error** | Check UC schema: `workshop_vibe_coding.TEAM_SCHEMA` |
| **Window function errors** | Verify `orderBy("month")` and `partitionBy("state", "industry")` |
| **XGBoost not installed** | `pip install xgboost` |
| **Model Serving 404** | Endpoint takes 5-10 min to provision. Check status in UI. |
| **Model Serving auth error** | Check `DATABRICKS_TOKEN` env var |
| **Low R² score** | Try XGBoost, add more features, or check for data leakage |

### DS Useful Commands

```bash
# MLflow
mlflow experiments list
mlflow runs list --experiment-id <id>

# Model Registry
databricks unity-catalog models list --catalog workshop_vibe_coding --schema TEAM_SCHEMA

# Model Serving
databricks serving-endpoints list
databricks serving-endpoints get grocery-forecast-TEAM_NAME
```

## Analyst Track

| Problem | Fix |
|---------|-----|
| **Can't find Genie in sidebar** | Ask facilitator — may need to be enabled |
| **Genie permission error** | Need CREATE GENIE SPACE on catalog |
| **Genie gives wrong SQL** | Add column descriptions + example queries to instructions |
| **Dashboard viz doesn't match** | Rephrase NL prompt or write SQL directly |
| **Column comments not showing** | Use `ALTER TABLE t ALTER COLUMN c COMMENT 'desc'` |
| **Dashboard slow** | Check SQL warehouse is running |
| **Embedded dashboard blank** | Users need Databricks credentials to view |

## Steering Tips

| When the agent... | Say this |
|-------------------|---------|
| Writes too much code | "Keep it simple. One function, minimal code." |
| Ignores your CLAUDE.md | "Read CLAUDE.md first, then try again." |
| Gets stuck in a loop | "Stop. Let's take a different approach. [describe what you want]" |
| Makes something overly complex | "Simplify this. I just need [specific thing]." |
| Writes code before tests | "Stop. Write the tests first, then implement." |
