## Step 6: Write the App PRD

Start Lab 2 by giving the agent a clear product spec.

### Prompt

Paste this into Claude Code:

```
Create a new directory called "app" and add a PRD as app/README.md:

## Grocery Intelligence App

### Overview
A web application that displays retail analytics from our gold tables
and lets users ask questions in plain English.

### User Stories
1. As a business user, I want to see retail turnover by state so I can compare performance.
2. As an analyst, I want to ask questions like "which state had the highest food retail growth?" and get answers.
3. As an executive, I want to see food inflation trends at a glance.

### Technical Requirements
- Backend: FastAPI (Python)
- Frontend: HTML + Tailwind CSS (CDN) + htmx (CDN) — no npm or node required
- Data: workshop_vibe_coding.TEAM_SCHEMA.retail_summary and food_inflation_yoy
- AI feature: Natural language to SQL using Databricks Foundation Model API
- Deployment: Databricks Apps

### API Endpoints
- GET /health → {"status": "ok"}
- GET /api/metrics?state=X&start_date=Y&end_date=Z → list of records
- POST /api/ask {"question": "..."} → {"answer": "...", "sql_query": "..."}
- GET / → serves the frontend HTML

### Tech Constraints
- Use databricks-sql-connector for all database queries
- All SQL must be parameterized (no string concatenation)
- Frontend uses Tailwind CSS from CDN and htmx from CDN — no build step
- Use Pydantic models for request/response validation

Also update CLAUDE.md to add these app-specific rules.
```

### Expected Result

An `app/README.md` with the PRD and updated `CLAUDE.md` with app-specific instructions.

### If It Doesn't Work

- **Agent creates too much:** Say "Just the PRD and CLAUDE.md update. Don't build anything yet."
- **Wrong directory:** Make sure the agent creates files inside the `app/` directory.
