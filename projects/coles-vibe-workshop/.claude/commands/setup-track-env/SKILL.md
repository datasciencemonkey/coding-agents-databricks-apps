---
name: setup-track-env
description: "Use when a team needs to set up their Python virtual environment for a workshop track (de, ds, or analyst). Creates an isolated uv venv under .venvs/ with all required dependencies pre-installed."
user-invocable: true
---

# Setup Track Environment

Create a pre-configured Python virtual environment for a workshop track using uv.

## Arguments

One required argument — the track name:

| Argument | Track | Key packages |
|----------|-------|-------------|
| `de` | Data Engineering | pyspark 4.1, delta-spark 4.1, beautifulsoup4, lxml |
| `ds` | Data Science | pyspark 4.1, mlflow 3.11, scikit-learn 1.8, xgboost 3.2 |
| `analyst` | Analyst | fastapi, uvicorn, sse-starlette, httpx |

All tracks also get: pytest, ruff, databricks-sdk, databricks-sql-connector.

## Process

### 1. Validate the argument

If no argument or invalid argument, print the table above and stop.

### 2. Ensure .venvs/ is gitignored

```bash
cd /app/python/source_code/projects/coles-vibe-workshop && grep -qxF '.venvs/' .gitignore || echo '.venvs/' >> .gitignore
```

### 3. Create the virtual environment

```bash
cd /app/python/source_code/projects/coles-vibe-workshop && /usr/local/bin/uv venv --python /usr/bin/python3.11 --clear .venvs/<TRACK>
```

If Python 3.11 is not found, fall back to `python3`:

```bash
cd /app/python/source_code/projects/coles-vibe-workshop && /usr/local/bin/uv venv --python python3 --clear .venvs/<TRACK>
```

### 4. Install dependencies

```bash
cd /app/python/source_code/projects/coles-vibe-workshop && /usr/local/bin/uv pip install -r requirements/<TRACK>.txt --python .venvs/<TRACK>/bin/python
```

If installation fails with a connection/network error, print:

```
Package installation failed — PyPI may be unreachable.

Ask the facilitator to allowlist these domains:
  pypi.org
  files.pythonhosted.org

To diagnose: curl -I https://pypi.org
```

### 5. Verify imports

Run the appropriate verification for the track:

**DE:**
```bash
.venvs/de/bin/python -c "
import pyspark; print(f'pyspark {pyspark.__version__}')
import pytest; print(f'pytest {pytest.__version__}')
import bs4; print('beautifulsoup4 OK')
import lxml; print('lxml OK')
print('--- DE environment ready ---')
"
```

Note: `databricks-declarative-pipelines` is NOT on public PyPI — it is only available on Databricks cluster runtime. The `@dp.table` / `@dp.expect` decorators will work when the pipeline runs on a cluster. For local testing, mock or skip those imports.

**DS:**
```bash
.venvs/ds/bin/python -c "
import pyspark; print(f'pyspark {pyspark.__version__}')
import mlflow; print(f'mlflow {mlflow.__version__}')
import sklearn; print(f'scikit-learn {sklearn.__version__}')
import xgboost; print(f'xgboost {xgboost.__version__}')
import pytest; print(f'pytest {pytest.__version__}')
print('--- DS environment ready ---')
"
```

**Analyst:**
```bash
.venvs/analyst/bin/python -c "
import fastapi; print(f'fastapi {fastapi.__version__}')
import uvicorn; print(f'uvicorn {uvicorn.__version__}')
import sse_starlette; print('sse-starlette OK')
import httpx; print(f'httpx {httpx.__version__}')
import pytest; print(f'pytest {pytest.__version__}')
print('--- Analyst environment ready ---')
"
```

### 6. Check Java (DE and DS only)

If the track is `de` or `ds`, check for Java since PySpark requires it:

```bash
java -version 2>&1 || echo "WARNING: Java not found — see note below."
```

### 7. Print activation instructions

```
Environment created: .venvs/<TRACK>/

Activate it:
  source .venvs/<TRACK>/bin/activate

Run tests:
  .venvs/<TRACK>/bin/python -m pytest tests/ -x --no-header -q

Or use directly without activating:
  .venvs/<TRACK>/bin/python your_script.py
```

## Important: PySpark in this environment

This Databricks App environment does **not** have Java installed. PySpark imports fine (`import pyspark` works), but `SparkSession.builder.getOrCreate()` will fail with `JAVA_GATEWAY_EXITED`.

**This is expected and OK for the workshop.** The DE and DS tracks write PySpark code that runs on Databricks clusters (via Lakeflow pipelines or notebooks), not locally. Teams should:
- Write and test pipeline logic using `pytest` with mocked Spark objects
- Deploy to Databricks clusters for actual Spark execution via `databricks bundle deploy`
- Use `databricks-sql-connector` for local data access when needed

Similarly, `databricks-declarative-pipelines` (`@dp.table`, `@dp.expect`) is only available on Databricks cluster runtime, not on public PyPI.

## Notes

- Running this skill again for the same track is safe — it recreates the venv cleanly.
- Teams can have multiple track venvs simultaneously.
- Requirements files are in `requirements/` and are version-controlled.
