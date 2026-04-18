# Lab 1: Build Your Data Pipeline (Data Engineering Track)

**Duration:** 55 minutes
**Goal:** Build, test, and deploy a Lakeflow Declarative Pipeline using an AI coding agent
**Team Size:** 2–3 people

> Complete `LAB-0-GETTING-STARTED.md` first, then return here.

---

## The Mission

Your team needs a data pipeline that ingests public Australian retail data, transforms it through a medallion architecture, and produces analytics-ready gold tables. You'll use **TDD** to guide the agent and **Lakeflow Declarative Pipelines** to define your tables.

**You will NOT write this code yourself.** You will direct an AI agent to build it.

---

## Your Data Sources

| Source | API Endpoint | What It Contains |
|--------|-------------|-----------------|
| **ABS Retail Trade** | `https://data.api.abs.gov.au/data/ABS,RT,1.0.0/...` | Monthly retail turnover by state & industry since 2010 |
| **ABS Consumer Price Index** | `https://data.api.abs.gov.au/data/ABS,CPI,2.0.0/...` | Quarterly food price indices by state since 2010 |

Both APIs return CSV data via the SDMX standard. The agent will handle the API calls and parsing.

---


---

## Phase 1: Write Tests First (15 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Run data exploration prompt from `starter-kit/prompts/01-explore-data.md`
> - **Person B (Terminal):** Copy `starter-kit/CLAUDE.md` to project root, customize team name/schema
> - **Person C (Databricks UI):** Open workspace, verify Unity Catalog schema exists, check checkpoint tables are accessible
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

> **Remember:** Tests are your spec. Write them BEFORE any implementation.

### 1.1 Explore the data

Ask the agent:

```
Fetch a sample of the ABS Retail Trade API:
https://data.api.abs.gov.au/data/ABS,RT,1.0.0/M1.20+41+42+43+44+45.20.1+2+3+4+5+6+7+8.M?format=csv&startPeriod=2024-01&endPeriod=2024-03

Show me the columns, data types, and a few sample rows.
Also fetch a sample of the ABS CPI Food API:
https://data.api.abs.gov.au/data/ABS,CPI,2.0.0/1.10001+20001.10.1+2+3+4+5+6+7+8.Q?format=csv&startPeriod=2024-Q1&endPeriod=2024-Q4

Show me the same for this one.
```

Understanding the raw data structure is critical before writing tests.

### 1.2 Write your pipeline tests

Ask the agent:

```
Create pytest tests for a Lakeflow Declarative Pipeline with these transformations:

1. test_bronze_retail_trade:
   - Raw CSV data is ingested with all original columns
   - Non-null TIME_PERIOD and OBS_VALUE columns
   - Test: given sample CSV rows, bronze table has correct schema

2. test_silver_retail_turnover:
   - REGION codes decoded to state names (1=NSW, 2=VIC, 3=QLD, etc.)
   - INDUSTRY codes decoded to readable names (20=Food retailing, etc.)
   - TIME_PERIOD parsed to proper date column
   - OBS_VALUE renamed to turnover_millions
   - Test: given bronze rows with codes, silver rows have readable names

3. test_gold_retail_summary:
   - Adds 3-month and 12-month rolling averages
   - Adds year-over-year growth percentage
   - Test: given 24 months of silver data, gold has correct rolling averages

4. test_bronze_cpi_food:
   - Raw CPI CSV data ingested with all columns
   - Non-null TIME_PERIOD and OBS_VALUE
   - Test: correct schema

5. test_silver_food_price_index:
   - REGION codes decoded to state names
   - INDEX codes decoded (10001=All groups CPI, 20001=Food and non-alcoholic beverages)
   - OBS_VALUE renamed to cpi_index
   - Test: codes correctly decoded

6. test_gold_food_inflation:
   - Calculates year-over-year CPI change percentage
   - Test: given 8 quarters of data, YoY change is correct

Write ONLY the tests. Do NOT implement the functions yet.
Use PySpark test fixtures with small DataFrames (5-10 rows each).
```

### 1.3 Review the tests

Read through the generated tests:
- Do they capture your transformation logic?
- Are the test data realistic?
- Are edge cases covered (nulls, missing periods)?

Edit or ask the agent to adjust before moving on.

> **Starter Kit:** Copy-paste prompts are in `starter-kit/prompts/01-explore-data.md` and `starter-kit/prompts/02-write-tests.md`

---

## Phase 2: Build Bronze Layer (15 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Build retail trade bronze table using `starter-kit/prompts/03-build-bronze.md`
> - **Person B (Terminal):** Build CPI food bronze table (same prompt covers both)
> - **Person C (Databricks UI):** Monitor Unity Catalog for new tables appearing, prepare checkpoint fallback if APIs fail
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 2.1 Create the pipeline structure

Ask the agent:

```
Create a Lakeflow Declarative Pipeline project with:
- src/bronze/abs_retail_trade.py - Ingest ABS Retail Trade API to bronze table
- src/bronze/abs_cpi_food.py - Ingest ABS CPI Food API to bronze table
- src/silver/ (empty for now)
- src/gold/ (empty for now)
- resources/pipeline.yml - Lakeflow pipeline definition
- databricks.yml - DABs deployment config
- tests/ (our tests from Phase 1)

For bronze tables, use @dp.table decorator with data quality expectations:
- @dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
- @dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")

Use spark.read.csv() to fetch from the API URLs.
Unity Catalog target: workshop_vibe_coding.<team_schema>
```

### 2.2 Run the bronze tests

```
Run the bronze tests. Fix any failures.
```

Watch the agent iterate: read test output → fix code → re-run → repeat until green.

> **Stuck?** If the API calls are failing (network issues, parsing errors), grab
> **Checkpoint 1A**: pre-loaded bronze tables are already in your schema.
> Tell the agent: "Use the pre-loaded tables in workshop_vibe_coding.checkpoints
> instead of calling the API. Copy them to our schema."

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/03-build-bronze.md`

---

## Phase 3: Build Silver + Gold (20 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Build silver retail_turnover and gold retail_summary
> - **Person B (Terminal):** Build silver food_price_index and gold food_inflation
> - **Person C (Databricks UI):** Monitor test output, review gold table data as it appears, prepare icebreaker answers
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 3.1 Build silver transformations

```
Implement the silver layer to make the silver tests pass:

1. src/silver/retail_turnover.py
   - @dp.table that reads from bronze retail trade
   - Decode REGION codes to state names: 1=New South Wales, 2=Victoria,
     3=Queensland, 4=South Australia, 5=Western Australia, 6=Tasmania,
     7=Northern Territory, 8=Australian Capital Territory
   - Decode INDUSTRY codes: 20=Food retailing, 41=Clothing/footwear/personal,
     42=Department stores, 43=Other retailing, 44=Cafes/restaurants/takeaway,
     45=Household goods retailing
   - Parse TIME_PERIOD to date, extract month/year/quarter
   - Rename OBS_VALUE to turnover_millions

2. src/silver/food_price_index.py
   - @dp.table that reads from bronze CPI
   - Decode REGION and INDEX codes
   - Rename OBS_VALUE to cpi_index

Run the silver tests after implementation.
```

### 3.2 Build gold materialized views

```
Implement the gold layer to make the gold tests pass:

1. src/gold/retail_summary.py
   - @dp.materialized_view
   - Join with silver retail_turnover
   - Add 3-month rolling average (turnover_3m_avg)
   - Add 12-month rolling average (turnover_12m_avg)
   - Add year-over-year growth percentage (yoy_growth_pct)

2. src/gold/food_inflation.py
   - @dp.materialized_view
   - Calculate year-over-year CPI change percentage (yoy_change_pct)

Run ALL tests (bronze + silver + gold). Everything should be green.
```

> **Stuck at 40 minutes?** Grab **Checkpoint 1B**: silver and gold tables
> pre-loaded in your schema. This ensures you have data for Lab 2.

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/04-build-silver-gold.md`

### 3.3 Verify your data

```
Query the gold tables and show me:
1. Top 5 states by food retail turnover (latest month)
2. Year-over-year food price inflation by state (latest quarter)
3. The state with the highest retail growth rate
```

**This is where you check your ice breaker predictions!**

---

## Phase 4: Deploy with DABs (5 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Run `databricks bundle validate` and `databricks bundle deploy`
> - **Person B (Databricks UI):** Verify pipeline appears in Workflows tab, tables visible in Unity Catalog
> - **Person C:** Query gold tables to check icebreaker prediction answers
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 4.1 Create the pipeline definition

```
Create resources/pipeline.yml that defines a Lakeflow Declarative Pipeline:
- Pipeline name: grocery-intelligence-<team_name>
- Serverless: true
- Libraries: all our src/ notebooks
- Catalog: workshop_vibe_coding
- Schema: <team_schema>

And update databricks.yml with:
- Dev target using our workshop catalog/schema
- The pipeline resource
```

### 4.2 Validate and deploy

```
Validate the bundle: databricks bundle validate
Deploy to dev: databricks bundle deploy -t dev
Run the pipeline: databricks bundle run grocery-intelligence-<team_name> -t dev
```

### 4.3 Verify in the workspace

Open the Databricks workspace UI and confirm:
- [ ] Pipeline appears in the Workflows tab
- [ ] Tables are visible in Unity Catalog
- [ ] Data quality expectations are passing

> **Stuck?** Grab **Checkpoint 1C**: complete pipeline code and databricks.yml.

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/05-deploy-pipeline.md`. Config template at `starter-kit/databricks.yml.template`.

---

## Pro Tips

> **Steering the agent effectively:**
>
> - If the agent uses pandas instead of PySpark, say **"use PySpark, not pandas"** and add it to CLAUDE.md
> - If the agent writes implementation before you have tests, say **"stop — write the tests first"**
> - If the agent goes off track, say **"stop, let's go back to the failing tests"**
> - Use **"show me the test output"** to see exactly what's failing
> - Say **"explain what this function does"** to verify the agent's logic
> - **Rotate the driver** every 20 min so everyone gets hands-on time
> - Use skills: try **`/commit`** to commit your work with a good message

---

## Success Criteria

- [ ] Tests written BEFORE implementation
- [ ] All tests pass (bronze, silver, gold)
- [ ] Pipeline uses `@dp.table` and `@dp.materialized_view` decorators
- [ ] Data quality expectations with `@dp.expect()`
- [ ] Gold tables have rolling averages and YoY metrics
- [ ] Deployed as a Lakeflow pipeline via DABs
- [ ] Can answer the ice breaker prediction questions from the data!

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **ABS API returns errors or times out** | The APIs can be slow. Grab **Checkpoint 1A** (pre-loaded bronze tables) and skip the API ingestion. |
| **Agent uses pandas instead of PySpark** | Add to CLAUDE.md: "Always use PySpark, never pandas". Remind the agent explicitly. |
| **Tests fail with SparkSession errors** | Ensure conftest.py creates a local SparkSession: `SparkSession.builder.master("local[*]").getOrCreate()` |
| **@dp.table decorator not found** | Make sure the import is: `import dlt` (for older runtimes) or `import databricks.declarative_pipelines as dp` |
| **Can't write to Unity Catalog** | Check your schema: `workshop_vibe_coding.<team_schema>`. Run `databricks auth status` to verify access. |
| **Pipeline deploy fails** | Validate first: `databricks bundle validate`. Check databricks.yml for syntax errors. |
| **Agent rewrites working code** | Say: "Don't change functions that are already passing tests. Only fix the failing ones." |
| **Running out of time** | Grab the next checkpoint. No shame — the goal is to have data for Lab 2 and a demo at the end. |

---

## Reflection Questions (for Show & Tell)

1. How much code did you write vs. the agent?
2. Where did TDD help the most?
3. What was your most interesting data insight?
4. Were your ice breaker predictions right?
