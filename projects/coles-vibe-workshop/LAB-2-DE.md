# Lab 2: Data Quality, New Sources & Scheduling (Data Engineering Track)

**Duration:** 55 minutes
**Goal:** Add data sources, implement data quality rules, and set up pipeline scheduling
**Team Size:** 2–3 people

> Complete `LAB-0-GETTING-STARTED.md` and `LAB-1-DE.md` first.

---

## The Mission

Your pipeline handles ABS retail and CPI data. Now make it production-grade: add a new data source (FSANZ food recalls), implement data quality rules across all tables, and set up automated scheduling.

---

## Phase 1: Add FSANZ Food Recalls (20 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Write tests for FSANZ ingestion (schema, non-nulls, date parsing)
> - **Person B (Terminal):** Build bronze + silver tables for FSANZ food recalls
> - **Person C (Databricks UI):** Monitor pipeline, verify new tables appear in Unity Catalog
>
> *Teams of 2: Person A writes tests, Person B implements + monitors.*

### 1.1 Write tests + build tables

```
Add a new data source — FSANZ food recalls:

1. Write tests first:
   - test_bronze_food_recalls_schema: has columns (product, category, issue, date, state, url)
   - test_bronze_food_recalls_not_null: product and date are never null
   - test_silver_food_recalls_dates: date strings parsed to proper DATE type
   - test_silver_food_recalls_states: state names normalized to match our state list

2. Build the tables:
   - src/bronze/fsanz_food_recalls.py: @dp.table ingesting FSANZ data
   - src/silver/food_recalls.py: @dp.table with cleaned dates, normalized states
   - Data source: https://www.foodstandards.gov.au/food-recalls/recalls
   - If website is blocked, read from: workshop_vibe_coding.checkpoints.fsanz_food_recalls

3. Run tests after implementation.
```

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/de/05-add-data-sources.md`

> **Stuck?** Grab **Checkpoint DE-2A**: FSANZ bronze + silver tables pre-loaded.

---

## Phase 2: Data Quality Rules (20 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Add data quality expectations across all bronze/silver/gold tables
> - **Person B (Terminal):** Build cross-source gold view joining retail + CPI + recalls
> - **Person C (Databricks UI):** Verify expectations appear in pipeline UI, check quality metrics
>
> *Teams of 2: Person A does quality rules, Person B does cross-source view + monitoring.*

### 2.1 Add quality expectations

```
Add data quality expectations across all pipeline tables:

Bronze tables:
- @dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
- @dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")
- @dp.expect("valid_date_range", "TIME_PERIOD >= '2010-01'")

Silver tables:
- @dp.expect_or_fail("valid_state", "state IN ('New South Wales','Victoria','Queensland','South Australia','Western Australia','Tasmania','Northern Territory','Australian Capital Territory')")
- @dp.expect("valid_turnover", "turnover_millions > 0")

Gold tables:
- @dp.expect("valid_yoy", "yoy_growth_pct BETWEEN -100 AND 500")
- @dp.expect("valid_rolling_avg", "turnover_3m_avg > 0")

Run all tests to verify nothing breaks.
```

### 2.2 Build cross-source gold view

```
Create a cross-source analysis view:
- src/gold/grocery_insights.py: @dp.materialized_view
- Joins retail_summary + food_inflation_yoy + food_recalls (if available)
- Columns: state, month, turnover_millions, yoy_growth_pct, cpi_yoy_change, recall_count
- Join retail (monthly) with CPI (quarterly) on state + quarter
- Left join recalls on state + month (recall_count may be 0)
```

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/de/06-data-quality.md`

---

## Phase 3: Scheduling + Deploy (10 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Add cron scheduling, validate, and deploy
> - **Person B (Databricks UI):** Verify pipeline schedule in Workflows tab
> - **Person C:** Test the full pipeline end-to-end
>
> *Teams of 2: Person A deploys, Person B verifies.*

### 3.1 Add scheduling

```
Add cron scheduling to our pipeline:

1. Update databricks.yml — add trigger:
   trigger:
     cron:
       quartz_cron_expression: "0 0 6 * * ?"
       timezone_id: "Australia/Sydney"

2. Validate: databricks bundle validate
3. Deploy: databricks bundle deploy -t dev
4. Show me the pipeline schedule.
```

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/de/07-scheduling.md`

---

## Phase 4: Verify + Prepare (5 min)

- Verify full pipeline with all sources in the Workflows UI
- Check data quality expectations are visible and passing
- Prepare demo: Show pipeline DAG, quality metrics, cross-source view, schedule

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **FSANZ website blocked** | Use checkpoint: `workshop_vibe_coding.checkpoints.fsanz_food_recalls` |
| **Web scraping errors** | Try RSS feed: `https://www.foodstandards.gov.au/rss/recalls` |
| **@dp.expect_or_fail stops pipeline** | Use `@dp.expect` (warn) first, upgrade after verifying |
| **Cross-source join duplicates** | Join on state + date range, not exact date (CPI is quarterly) |
| **Cron not triggering** | Check timezone_id and Quartz format. `?` is required for day-of-week. |
| **Pipeline too slow** | Use `spark.conf.set("spark.sql.shuffle.partitions", "4")` for workshop |
| **Running out of time** | Grab Checkpoint DE-2C (complete pipeline) or DE-2D (full solution) |

---

## Success Criteria

- [ ] FSANZ food recalls ingested (bronze + silver)
- [ ] Data quality expectations on all tables
- [ ] Cross-source gold view joining retail + CPI + recalls
- [ ] Pipeline scheduled with cron trigger
- [ ] All tests pass including new data source
- [ ] Ready for 3-minute demo

---

## Reflection Questions (for Demo)

1. How do data quality expectations change your confidence in the pipeline?
2. What challenges came with adding a new data source?
3. How would you monitor this pipeline in production?
4. What's the most interesting insight from the cross-source view?
