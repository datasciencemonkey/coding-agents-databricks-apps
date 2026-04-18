# Lab 0: Getting Started (All Tracks)

**Duration:** 10 minutes
**Goal:** Set up your project, explore the data, and choose your track

---

## Step 1: Open Your Terminal

Your Coding Agents app gives you a browser-based terminal with Claude Code pre-installed. Open it in your browser now.

---

## Step 2: Set Up Your Project (Rule #1: Just Say What You Want)

Don't write config files by hand — have a conversation. Tell Claude about your project and it will create everything.

1. Create your project directory:
   ```bash
   mkdir -p grocery-intelligence && cd grocery-intelligence
   ```

2. Tell Claude about your project — just say it:

   ```
   I'm building a grocery intelligence platform on Databricks.
   Tech stack: PySpark, Lakeflow Declarative Pipelines, FastAPI + React, DABs.
   Data sources: ABS SDMX APIs, FSANZ web scraping, ACCC PDF ingestion via UC Volumes.
   Unity Catalog namespace: workshop_vibe_coding.<team_schema>.
   Set up the project and create a CLAUDE.md.
   ```

   Replace `<team_schema>` with your assigned value (e.g., `team_01`).

3. Review what Claude created — want to change something? Just say it:
   - "Add a rule that we always use PySpark, never pandas"
   - "Add our team angle: Retail Performance"
   - "Set up the test directory with conftest.py"

4. Copy your track's test stubs:

   | Track | Command |
   |-------|---------|
   | **Data Engineering** | `cp ~/starter-kit/test_pipeline.py tests/` |
   | **Data Science** | `cp ~/starter-kit/test_features.py tests/` |
   | **Analyst** | *(minimal tests — most work is UI-based)* |

---

## Step 3: Verify Your Environment

```bash
# Check Claude Code is working
claude --version

# Check Databricks CLI
databricks auth status

# Check your Unity Catalog access
databricks catalogs list | grep workshop
```

If any of these fail, ask the facilitator for help.

---

## Step 4: Explore the Data

All tracks use the same gold tables. Paste this into Claude Code:

```
Query these tables and show me 5 rows from each:
- workshop_vibe_coding.checkpoints.retail_summary
- workshop_vibe_coding.checkpoints.food_inflation_yoy

Tell me: what columns are available, what date range is covered, and which states are included.
```

This gives you a feel for the data regardless of your track.

---

## Step 5: Choose Your Track

| Track | You'll Build | Best For |
|-------|-------------|----------|
| **Data Engineering** | Lakeflow pipeline (Bronze→Silver→Gold), DABs deployment, data quality | Teams who want to build the data foundation |
| **Data Science** | Feature engineering, MLflow experiments, model training + serving | Teams who want to build ML models from the data |
| **Analyst** | Genie spaces, AI/BI dashboards, FastAPI web app | Teams who want to build interfaces for business users |

All tracks connect to the same data — you're building different layers of the same platform.

---

## Now Go To Your Track

- **Data Engineering** → `LAB-1-DE.md`
- **Data Science** → `LAB-1-DS.md`
- **Analyst** → `LAB-1-ANALYST.md`
