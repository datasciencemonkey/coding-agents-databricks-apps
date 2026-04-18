## Track: Analyst

### Data Source
- Read from gold tables: `workshop_vibe_coding.TEAM_SCHEMA.retail_summary` and `food_inflation_yoy`
- These are pre-loaded in checkpoints — no need to build the pipeline

### Genie Spaces
- Create via Databricks UI: Genie → New Genie Space
- Add gold tables and write clear general instructions
- Column descriptions in Unity Catalog improve Genie accuracy significantly
- Test with varied natural language questions

### AI/BI Dashboards
- Create via Databricks UI: Dashboards → Create → AI/BI Dashboard
- Use natural language prompts to describe each visualization
- Arrange into a clean layout with title and filters
- Publish and get embed URL for app integration

### Web Application
- Backend: FastAPI with Pydantic models
- Frontend: HTML + Tailwind CSS (CDN) + htmx (CDN) — no npm/node required
- Database: databricks-sql-connector with parameterized queries only
- AI feature: Foundation Model API for natural language to SQL
- Deployment: Databricks Apps with `app.yaml`

### Embedding Dashboards
- Published dashboards can be embedded via iframe
- `<iframe src="EMBED_URL" width="100%" height="600px"></iframe>`
- Users need Databricks credentials to view embedded dashboards
