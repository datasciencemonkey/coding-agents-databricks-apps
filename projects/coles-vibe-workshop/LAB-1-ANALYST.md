# Lab 1: Genie Spaces & AI/BI Dashboards (Analyst Track)

**Duration:** 55 minutes
**Goal:** Create Genie spaces, build AI/BI dashboards, and tune with metadata
**Team Size:** 2–3 people

> Complete `LAB-0-GETTING-STARTED.md` first, then return here.

---

## The Mission

Your gold tables are pre-loaded (from checkpoints). Build natural language interfaces that let business users query this data without writing code.

**Most of this lab is in the Databricks UI.** The terminal is used for adding metadata and writing SQL.

---

## Phase 1: Create Genie Space + Add Metadata (15 min)

> **Team Tasks for This Phase**
> - **Person A (Databricks UI):** Create Genie space with gold tables and instructions
> - **Person B (Databricks UI):** Navigate to AI/BI Dashboards, start first visualization
> - **Person C (Terminal):** Add column descriptions to gold tables in Unity Catalog
>
> *Teams of 2: Person A does UI tasks, Person B does Terminal + UI.*

### 1.1 Create your Genie space (Person A)

In the Databricks workspace UI:

1. Click **Genie** in the left sidebar
2. Click **New Genie Space**
3. Configure:
   - **Name:** "Grocery Intelligence — TEAM_NAME"
   - **SQL Warehouse:** Select the workshop warehouse
   - **Tables:** Add:
     - `workshop_vibe_coding.TEAM_SCHEMA.retail_summary`
     - `workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy`
   - **General Instructions:** Paste this:
     ```
     This data contains Australian retail trade and food price data.
     States are Australian states (New South Wales, Victoria, Queensland, etc.).
     Turnover is in millions of AUD.
     CPI index values are relative to a base period.
     YoY growth and change percentages show year-over-year comparisons.
     ```

### 1.2 Add column descriptions (Person C)

Paste this into Claude Code:

```
Add column comments to our gold tables for better Genie and AI/BI accuracy:

For workshop_vibe_coding.TEAM_SCHEMA.retail_summary:
- Table comment: "Monthly retail turnover summary by Australian state and industry with rolling averages and YoY growth"
- state: "Australian state name (New South Wales, Victoria, Queensland, etc.)"
- industry: "Retail industry category (Food retailing, Department stores, etc.)"
- month: "Date of the monthly observation (first of month)"
- turnover_millions: "Monthly retail turnover in millions of AUD"
- turnover_3m_avg: "3-month rolling average of turnover in millions AUD"
- turnover_12m_avg: "12-month rolling average of turnover in millions AUD"
- yoy_growth_pct: "Year-over-year turnover growth as a percentage"

For workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy:
- Table comment: "Quarterly food price inflation by Australian state with YoY CPI changes"
- state: "Australian state name"
- quarter: "Calendar quarter"
- cpi_index: "Consumer Price Index value (base period = 100)"
- yoy_change_pct: "Year-over-year CPI change as a percentage (positive = inflation)"

Use ALTER TABLE ... SET TBLPROPERTIES for table comments.
Use ALTER TABLE ... ALTER COLUMN ... COMMENT for column comments.
```

> **Starter Kit:** Steps in `starter-kit/prompts/analyst/01-setup-genie.md` and `analyst/02-tune-genie.md`

---

## Phase 2: Build AI/BI Dashboard (20 min)

> **Team Tasks for This Phase**
> - **Person A (Databricks UI):** Create 4-5 dashboard visualizations using NL prompts
> - **Person B (Databricks UI):** Test Genie with challenging questions, refine instructions
> - **Person C (Terminal):** Write SQL queries for complex visualizations the NL can't generate well
>
> *Teams of 2: Person A does dashboards, Person B does Genie + SQL.*

### 2.1 Create dashboard (Person A)

In the Databricks UI:

1. Navigate to **Dashboards** → **Create Dashboard** → **AI/BI Dashboard**
2. Connect to your gold tables
3. Use these natural language prompts:

```
Show monthly food retail turnover by state as a line chart for the last 2 years
```

```
Create a bar chart comparing year-over-year retail growth by state for the latest month
```

```
Show a heatmap of food inflation by state and quarter
```

```
Display the top 5 states by average monthly turnover as a horizontal bar chart
```

```
Show a trend line of national food price inflation over time
```

4. Arrange into a clean layout
5. Title: "Grocery Intelligence Dashboard — TEAM_NAME"

### 2.2 Test Genie (Person B)

Try these questions and note which ones Genie gets right:

- "Which state had the highest food retail turnover last month?"
- "Show me the year-over-year food price inflation trend for Victoria"
- "Compare retail growth across all states for the last 12 months"
- "What's the average monthly turnover for department stores in NSW?"
- "Which industry has the fastest growing turnover nationally?"

If Genie gets a question wrong, refine the General Instructions.

> **Starter Kit:** Dashboard steps in `starter-kit/prompts/analyst/03-build-dashboard.md`

> **Stuck?** Grab **Checkpoint AN-1B**: dashboard with 3 pre-built visualizations.

---

## Phase 3: Polish + Advanced Tuning (15 min)

> **Team Tasks for This Phase**
> - **Person A:** Refine Genie instructions — add example queries, clarify ambiguous terms
> - **Person B:** Polish dashboard layout, add filters, publish
> - **Person C:** Test Genie with 10 sample questions, document accuracy rate
>
> *Teams of 2: Split between Genie tuning and dashboard polishing.*

### 3.1 Tune Genie accuracy

Based on testing, update General Instructions with:
- Example questions and expected SQL patterns
- Clarifications for ambiguous terms (e.g., "last month" = most recent month in data)
- Specific column mappings for common questions

### 3.2 Publish dashboard

1. Click **Publish** on your dashboard
2. Click **Share** → get the URL for your demo
3. Optionally click **Embed** → copy iframe code (for Lab 2 app integration)

---

## Phase 4: Verify + Prepare (5 min)

- Test 5 sample questions against Genie — aim for 80%+ accuracy
- Review dashboard — all visualizations render, filters work
- Prepare for Show & Tell: What did you build? What was Genie best/worst at?

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Can't find Genie in sidebar** | Ask facilitator — Genie may need to be enabled |
| **"No permission" for Genie** | Need CREATE GENIE SPACE permission. Ask facilitator. |
| **Genie gives wrong SQL** | Add column descriptions and example queries to instructions |
| **AI/BI dashboard slow** | Check SQL warehouse is running (Compute → SQL Warehouses) |
| **Dashboard viz doesn't match** | Rephrase the NL prompt or write SQL directly |
| **Column descriptions not showing** | Run ALTER TABLE with correct syntax (see starter-kit prompt) |
| **Running out of time** | Grab Checkpoint AN-1B (dashboard) or AN-1C (complete solution) |

---

## Success Criteria

- [ ] Genie space created with gold tables and instructions
- [ ] Gold tables have column descriptions in Unity Catalog
- [ ] AI/BI dashboard has at least 4 visualizations
- [ ] Genie answers 7/10 test questions correctly
- [ ] Dashboard published with clean layout
- [ ] Ready for Show & Tell

---

## Reflection Questions (for Show & Tell)

1. How did column descriptions affect Genie's accuracy?
2. Which questions was Genie best/worst at answering?
3. How does this compare to building a custom query interface?
4. What would you do differently with more time?
