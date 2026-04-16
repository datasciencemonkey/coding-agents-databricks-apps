# Lab 1: Feature Engineering & MLflow (Data Science Track)

**Duration:** 55 minutes
**Goal:** Build a feature engineering pipeline from gold tables and track experiments with MLflow
**Team Size:** 2–3 people

> Complete `LAB-0-GETTING-STARTED.md` first, then return here.

---

## The Mission

Your gold tables are pre-loaded (from checkpoints). Build a feature engineering pipeline that creates lag features, seasonal indicators, and growth rates — then track everything with MLflow to prepare for model training in Lab 2.

**You will NOT write this code yourself.** You will direct an AI agent to build it.

---

## Phase 1: Explore Data + Write Tests (15 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Query gold tables, understand distributions and patterns
> - **Person B (Terminal):** Write pytest tests for feature engineering functions
> - **Person C (Databricks UI):** Create MLflow experiment in workspace, verify tracking works
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 1.1 Explore the gold tables

Paste this into Claude Code:

```
Query these tables and show me a comprehensive analysis:

1. workshop_vibe_coding.TEAM_SCHEMA.retail_summary:
   - Row count, date range, distinct states, distinct industries
   - Summary statistics for turnover_millions (min, max, mean, stddev)
   - Top 5 state-industry combinations by average turnover

2. workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy:
   - Row count, date range, distinct states
   - Summary statistics for yoy_change_pct
   - States with highest and lowest inflation

Show me the results as tables.
```

### 1.2 Write feature engineering tests

```
Create pytest tests for feature engineering in tests/test_features.py.
Use the fixtures from tests/conftest.py.

Write these tests:

1. test_create_lag_features:
   - Given 24 months of data for one state/industry
   - Creates turnover_lag_1m, turnover_lag_3m, turnover_lag_6m, turnover_lag_12m
   - lag_1m equals previous month's value
   - First 12 rows have null lag_12m (expected)

2. test_create_seasonal_features:
   - Adds month_of_year (1-12), quarter (1-4), is_december (boolean), is_q4 (boolean)
   - is_december is True only for month 12

3. test_create_growth_features:
   - Adds turnover_mom_growth and turnover_yoy_growth
   - MoM growth = (current - previous) / previous * 100
   - YoY growth = (current - 12m_ago) / 12m_ago * 100

4. test_feature_table_schema:
   - Output has all expected columns
   - Key columns (state, industry, month, turnover_millions) have no nulls

Write ONLY the tests. Do NOT implement the functions yet.
Use PySpark test fixtures with small DataFrames.
```

> **Starter Kit:** Copy-paste prompts in `starter-kit/prompts/ds/01-explore-gold.md` and `ds/02-feature-engineering.md`. Test stubs at `starter-kit/test_features.py`.

---

## Phase 2: Build Feature Engineering Pipeline (20 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Build lag and seasonal feature functions
> - **Person B (Terminal):** Build growth rate features and combine into feature table
> - **Person C (Databricks UI):** Run EDA — distribution plots, correlation analysis, trend identification
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 2.1 Build features

```
Create a feature engineering pipeline that reads from our gold tables and produces a feature table.

1. Lag features from retail_summary:
   - turnover_lag_1m, turnover_lag_3m, turnover_lag_6m, turnover_lag_12m
   - Use PySpark Window functions partitioned by state + industry, ordered by month

2. Seasonal features:
   - month_of_year (1-12), quarter (1-4), is_december (boolean), is_q4 (boolean)
   - Extract from the month date column

3. Growth rate features:
   - turnover_mom_growth: month-over-month growth percentage
   - turnover_yoy_growth: year-over-year growth percentage
   - cpi_yoy_change: join with food_inflation_yoy on state + quarter

4. Write the combined feature table to:
   workshop_vibe_coding.TEAM_SCHEMA.retail_features

Run tests after implementation. Handle nulls in lag features (first N rows will be null — filter them out in the final table).
```

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/ds/02-feature-engineering.md`

> **Stuck at 35 minutes?** Grab **Checkpoint DS-1B**: pre-built feature table in your schema.

---

## Phase 3: MLflow Experiment Tracking (15 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Log feature engineering run to MLflow with parameters, metrics, artifacts
> - **Person B (Terminal):** Create and log visualizations (correlation heatmap, trend plots)
> - **Person C (Databricks UI):** Review experiment in MLflow UI, compare runs, tag experiment
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 3.1 Track experiments

```
Set up MLflow experiment tracking for our feature engineering:

1. Create an MLflow experiment named "grocery-features-TEAM_NAME"

2. Log a run with:
   - Parameters: number of features, date range, number of states
   - Metrics: feature table row count, null percentage per feature
   - Tags: team_name, track="data_science", phase="feature_engineering"
   - Artifacts: save a feature summary CSV showing stats per state

3. Create and log visualizations:
   - A correlation heatmap of the numeric features (save as PNG)
   - A time series plot of turnover trends for top 3 states (save as PNG)

Use mlflow.log_param(), mlflow.log_metric(), mlflow.log_artifact().
Show me the MLflow experiment URL when done.
```

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/ds/03-mlflow-experiment.md`

---

## Phase 4: Verify + Prepare (5 min)

- Verify feature table in Unity Catalog browser
- Review MLflow experiment UI — runs, metrics, artifacts
- Prepare for Show & Tell: What features did you create? What patterns did you find?

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **MLflow tracking URI errors** | Check `DATABRICKS_HOST` env var is set: `echo $DATABRICKS_HOST` |
| **Feature table write permission** | Check UC schema access: `workshop_vibe_coding.TEAM_SCHEMA` |
| **Window function errors** | Verify orderBy uses a date column and partitionBy uses state + industry |
| **Pandas vs PySpark confusion** | Start with PySpark; collect to pandas only for small viz DataFrames |
| **Null values in lag features** | Expected for first N rows. Filter with `.dropna()` in the final table |
| **Agent uses pandas for features** | Say: "Use PySpark Window functions, not pandas. Check CLAUDE.md." |
| **MLflow experiment not found** | Set experiment explicitly: `mlflow.set_experiment("/Users/.../grocery-features")` |
| **Running out of time** | Grab Checkpoint DS-1B (feature table) or DS-1C (with MLflow experiment) |

---

## Success Criteria

- [ ] Feature table has lag, seasonal, and growth features
- [ ] All feature engineering tests pass
- [ ] MLflow experiment logged with parameters, metrics, artifacts
- [ ] At least one visualization logged as artifact
- [ ] Feature table accessible in Unity Catalog
- [ ] Ready for Show & Tell

---

## Reflection Questions (for Show & Tell)

1. Which features do you think will be most predictive for forecasting?
2. How did MLflow help organize your experimentation?
3. What additional data sources would improve your features?
4. Were there any surprising patterns in the data?
