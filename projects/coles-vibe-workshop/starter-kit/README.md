# Starter Kit

Everything you need to get started. Follow these steps in order.

## Track Selection

Before setup, your team picks one of three tracks:

| Track | Focus | Key Files |
|-------|-------|-----------|
| **Data Engineering (DE)** | Lakeflow pipeline (Bronze→Silver→Gold) | `CLAUDE-de.md`, `test_pipeline.py`, `prompts/de/` |
| **Data Science (DS)** | Feature engineering, MLflow, model serving | `CLAUDE-ds.md`, `test_features.py`, `test_model.py`, `prompts/ds/` |
| **Analyst** | Genie spaces, AI/BI dashboards, FastAPI app | `CLAUDE-analyst.md`, `test_app.py`, `prompts/analyst/` |

## Setup (5 minutes)

1. **Copy CLAUDE.md** to your project root:
   ```bash
   cp starter-kit/CLAUDE.md ./CLAUDE.md
   ```
   Then edit `CLAUDE.md` and replace `TEAM_SCHEMA` with your team schema (e.g., `team_01`)

2. **Append your track's CLAUDE extension:**
   ```bash
   # Data Engineering track
   cat starter-kit/CLAUDE-de.md >> ./CLAUDE.md

   # Data Science track
   cat starter-kit/CLAUDE-ds.md >> ./CLAUDE.md

   # Analyst track
   cat starter-kit/CLAUDE-analyst.md >> ./CLAUDE.md
   ```

3. **Copy test files** to your tests directory:
   ```bash
   mkdir -p tests
   cp starter-kit/conftest.py tests/

   # Data Engineering track
   cp starter-kit/test_pipeline.py tests/

   # Data Science track
   cp starter-kit/test_features.py tests/
   cp starter-kit/test_model.py tests/

   # Analyst track
   cp starter-kit/test_app.py tests/
   ```

4. **Follow the prompts** in your track's folder — they're numbered in order:
   - DE track: `starter-kit/prompts/de/` (pipeline phases)
   - DS track: `starter-kit/prompts/ds/` (features → training → serving)
   - Analyst track: `starter-kit/prompts/analyst/` (Genie → dashboard → app)
   - Each prompt is exact copy-paste into Claude Code

5. **If stuck**, check `starter-kit/cheatsheet.md` for quick fixes

## What's in Here

| File | What it is |
|------|-----------|
| `CLAUDE.md` | Shared project instructions for the AI agent — drop into project root |
| `CLAUDE-de.md` | DE track extension — Lakeflow, medallion architecture rules |
| `CLAUDE-ds.md` | DS track extension — MLflow, feature engineering, model serving rules |
| `CLAUDE-analyst.md` | Analyst track extension — Genie, AI/BI, FastAPI + htmx rules |
| `conftest.py` | pytest fixtures with SparkSession and sample data |
| `test_pipeline.py` | DE track test stubs (pipeline tests) |
| `test_features.py` | DS track test stubs (feature engineering tests) |
| `test_model.py` | DS track test stubs (model training/serving tests) |
| `test_app.py` | Analyst track test stubs (API + app tests) |
| `databricks.yml.template` | Databricks Asset Bundle config |
| `app.yaml.template` | Databricks Apps deployment config |
| `cheatsheet.md` | Quick fixes for common problems (all tracks) |
| `prompts/de/` | Exact copy-paste prompts for DE track |
| `prompts/ds/` | Exact copy-paste prompts for DS track |
| `prompts/analyst/` | Exact copy-paste prompts for Analyst track |
