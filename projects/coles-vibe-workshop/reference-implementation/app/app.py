"""Grocery Intelligence Platform — FastAPI application.

Serves a dashboard for Australian retail trade and food price analytics.
Queries gold-layer tables in Unity Catalog via databricks-sql-connector.
"""

import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from databricks import sql as databricks_sql


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
SQL_WAREHOUSE_ID = os.environ.get("SQL_WAREHOUSE_ID", "")
CATALOG = os.environ.get("CATALOG", "workshop_vibe_coding")
SCHEMA = os.environ.get("SCHEMA", "reference")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def _get_connection():
    """Return a new databricks-sql-connector connection."""
    return databricks_sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=f"/sql/1.0/warehouses/{SQL_WAREHOUSE_ID}",
        access_token=DATABRICKS_TOKEN,
    )


def _query(sql: str, params: dict | None = None) -> list[dict]:
    """Execute *sql* and return rows as a list of dicts."""
    with _get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql, params)
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Grocery Intelligence Platform", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (index.html, etc.)
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))


@app.get("/api/metrics")
async def metrics():
    """Return headline KPIs from gold tables."""
    try:
        top_states = _query(f"""
            SELECT state, ROUND(SUM(turnover_millions), 1) AS total_turnover
            FROM {CATALOG}.{SCHEMA}.retail_summary
            WHERE month >= ADD_MONTHS(CURRENT_DATE(), -12)
            GROUP BY state
            ORDER BY total_turnover DESC
            LIMIT 5
        """)

        monthly_trend = _query(f"""
            SELECT month, ROUND(SUM(turnover_millions), 1) AS national_turnover
            FROM {CATALOG}.{SCHEMA}.retail_summary
            WHERE month >= ADD_MONTHS(CURRENT_DATE(), -12)
            GROUP BY month
            ORDER BY month
        """)

        yoy_row = _query(f"""
            SELECT ROUND(AVG(yoy_growth_pct), 2) AS avg_yoy_growth
            FROM {CATALOG}.{SCHEMA}.retail_summary
            WHERE month = (
                SELECT MAX(month) FROM {CATALOG}.{SCHEMA}.retail_summary
            )
        """)

        inflation_row = _query(f"""
            SELECT ROUND(AVG(yoy_change_pct), 2) AS avg_food_inflation
            FROM {CATALOG}.{SCHEMA}.food_inflation_yoy
            WHERE quarter = (
                SELECT MAX(quarter) FROM {CATALOG}.{SCHEMA}.food_inflation_yoy
            )
        """)

        return {
            "top_states": top_states,
            "monthly_trend": [
                {"month": str(r["month"]), "national_turnover": r["national_turnover"]}
                for r in monthly_trend
            ],
            "yoy_growth": yoy_row[0]["avg_yoy_growth"] if yoy_row else None,
            "food_inflation": inflation_row[0]["avg_food_inflation"] if inflation_row else None,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/recalls")
async def recalls():
    """Return recent food recalls from gold table."""
    try:
        rows = _query(f"""
            SELECT product, category, issue, date, state, url
            FROM {CATALOG}.{SCHEMA}.food_recalls_clean
            ORDER BY date DESC
            LIMIT 20
        """)
        return [
            {k: str(v) if v is not None else None for k, v in row.items()}
            for row in rows
        ]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/ask")
async def ask(request: Request):
    """Accept a natural language question, generate SQL via Foundation Model API, execute it."""
    body = await request.json()
    question = body.get("question", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    # Build a prompt that constrains the model to generate valid SQL
    system_prompt = f"""You are a SQL assistant for Australian grocery retail data.
Available tables in catalog `{CATALOG}`, schema `{SCHEMA}`:

1. retail_summary (state STRING, industry STRING, month DATE, turnover_millions DOUBLE,
   turnover_3m_avg DOUBLE, turnover_12m_avg DOUBLE, yoy_growth_pct DOUBLE)
2. food_inflation_yoy (state STRING, quarter DATE, cpi_index DOUBLE, yoy_change_pct DOUBLE)

Rules:
- Return ONLY a single SQL SELECT statement, nothing else.
- Use fully qualified table names: {CATALOG}.{SCHEMA}.<table>.
- Never use DROP, DELETE, INSERT, UPDATE, or ALTER.
"""

    try:
        # Use the Foundation Model API via databricks-sql-connector
        sql_gen_query = f"""
            SELECT ai_query(
                'databricks-dbrx-instruct',
                CONCAT('{system_prompt.replace("'", "''")}', '\\nQuestion: ', :question)
            ) AS generated_sql
        """
        result = _query(sql_gen_query, {"question": question})
        generated_sql = result[0]["generated_sql"].strip() if result else ""

        # Basic safety check
        forbidden = ["DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "GRANT", "REVOKE"]
        if any(kw in generated_sql.upper() for kw in forbidden):
            raise HTTPException(status_code=400, detail="Generated SQL contains forbidden operations")

        # Execute the generated SQL
        rows = _query(generated_sql)
        return {
            "question": question,
            "sql": generated_sql,
            "results": [
                {k: str(v) if v is not None else None for k, v in row.items()}
                for row in rows
            ],
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
