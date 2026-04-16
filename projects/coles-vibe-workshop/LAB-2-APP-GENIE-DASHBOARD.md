# Lab 2: Build Your App, Genie Space & Dashboard

**Duration:** 55 minutes
**Goal:** Build a web app with AI features, create a Genie space, and set up an AI/BI dashboard
**Team Size:** 2–3 people

---

## The Mission

Your pipeline is producing analytics-ready gold tables. Now put that data to work. **Pick your tier:**

### Tier 1: Quick — Embed & Ship (~20 min)
FastAPI backend + **embedded AI/BI dashboard via iframe**. Publish your dashboard, drop the embed URL into your app. Polished result, minimal frontend code.

### Tier 2: Medium — Custom Charts (~35 min)
FastAPI + React with **Recharts** or **Observable Plot**. Query gold tables via API, render interactive visualisations in the browser.

### Tier 3: Stretch — Full Platform (~55 min)
Full React app with custom viz + **embedded dashboard** + Genie space + NL query feature. The whole enchilada.

**All tiers also include:**
- **A Genie space** — natural language Q&A for business users (2 min to set up!)
- **An AI/BI dashboard** — auto-generated visualisations (can be embedded in your app)

All connect to the same gold tables from Lab 1. **You will direct the AI agent to build everything.**

---

## Getting Started (2 minutes)

1. Create the app directory:
   ```bash
   mkdir -p app/static
   ```

2. Copy the app config template:
   ```bash
   cp starter-kit/app.yaml.template app/app.yaml
   ```
   Replace `REPLACE_WITH_SQL_WAREHOUSE_PATH` with your SQL warehouse path.

3. Your CLAUDE.md from Lab 1 already has the project context. The PRD prompt will add app-specific rules.

> All prompts for this lab are in `starter-kit/prompts/06-11`. Each is exact copy-paste.
>
> **Key insight:** Person C can start the Genie space and AI/BI dashboard immediately in the Databricks UI while Persons A and B work in terminals. This saves significant time.

---

## Architecture

```
┌───────────────┐     HTTP       ┌──────────────────────┐
│               │  (htmx calls)  │                      │
│   Browser     │───────────────▶│   FastAPI Backend     │
│  (Tailwind    │◀───────────────│   (app.py)           │
│   + htmx)     │  HTML / JSON   │                      │
│               │                │  GET /api/metrics     │
└───────────────┘                │  POST /api/ask        │
                                 │  GET /                │
                                 └──────┬───────┬───────┘
                                        │       │
                                SQL     │       │  LLM
                                queries │       │  prompt
                                        ▼       ▼
                                 ┌────────┐ ┌──────────┐
                                 │SQL     │ │Databricks│
                                 │Warehou-│ │Foundation│
                                 │se      │ │Model API │
                                 └────────┘ └──────────┘

    ┌─────────────────┐         ┌─────────────────────┐
    │  Genie Space    │         │  AI/BI Dashboard     │
    │  (NL queries    │         │  (Auto-generated     │
    │   on gold data) │         │   visualizations)    │
    └─────────────────┘         └─────────────────────┘
```

---

## Phase 1: Write PRD + Tests (10 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Run PRD prompt from `starter-kit/prompts/06-write-prd.md`
> - **Person B (Terminal):** Run API test prompt from `starter-kit/prompts/07-write-app-tests.md`
> - **Person C (Databricks UI):** Start creating Genie space NOW (follow `starter-kit/prompts/10-setup-genie.md`) — this is a UI task that doesn't need the terminal
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

> **Starter Kit:** Copy-paste prompts in `starter-kit/prompts/06-write-prd.md` and `07-write-app-tests.md`. Genie setup steps in `10-setup-genie.md`.

### 1.1 Write your app PRD

Tell the agent:

```
Create a new project called "grocery-app" with this PRD:

## Grocery Intelligence App

### Overview
A web application that displays retail analytics from our gold tables
and allows natural language querying of the data.

### User Stories
1. As a business user, I want to see retail turnover by state in a
   clean dashboard with filters.
2. As an analyst, I want to ask questions in plain English like
   "which state had the highest food retail growth last year?"
3. As an executive, I want to see food inflation trends at a glance.

### Technical Requirements
- Backend: FastAPI (Python)
- Frontend: HTML + Tailwind CSS + htmx (no npm/node required)
- Data: workshop_vibe_coding.<team_schema>.retail_summary
  and workshop_vibe_coding.<team_schema>.food_inflation_yoy
- AI feature: Natural language to SQL using Foundation Model API
- Deployment: Databricks Apps

### API Endpoints
- GET /api/metrics?state=X&start_date=Y&end_date=Z
- POST /api/ask {"question": "which state has highest growth?"}
- GET /health → {"status": "ok"}
- GET / (serves the frontend)

Also create a CLAUDE.md with:
- Use FastAPI with Pydantic models
- Use databricks-sql-connector for database access
- Frontend uses htmx for dynamic updates (no JS frameworks)
- Write tests for all API endpoints using pytest + httpx
- All SQL queries must be parameterized (no string concatenation)
```

### 1.2 Write API tests

```
Write pytest tests for the FastAPI backend:

1. test_health: GET /health returns 200 with {"status": "ok"}

2. test_get_metrics:
   - Returns 200 with valid state and date range
   - Returns list of records with: state, industry, month,
     turnover_millions, yoy_growth_pct
   - Returns 400 for invalid date format
   - Returns empty list for non-existent state

3. test_ask_question:
   - Returns 200 with a valid question
   - Response has: answer (string), sql_query (string)
   - Returns 400 for empty question

Write ONLY the tests. Do NOT implement yet.
Use httpx AsyncClient with ASGITransport for testing.
```

### 1.3 Create your Genie space (Person C)

Genie is Databricks' natural language Q&A interface. Business users type questions in plain English, Genie generates SQL, and returns results with visualizations. No code required.

In the Databricks workspace UI (not the terminal):

1. Navigate to **Genie** in the left sidebar
2. Click **New Genie Space**
3. Configure:
   - **Name:** "Grocery Intelligence — Team [your_team]"
   - **SQL Warehouse:** Select the workshop warehouse
   - **Tables:** Add your gold tables:
     - `workshop_vibe_coding.<team_schema>.retail_summary`
     - `workshop_vibe_coding.<team_schema>.food_inflation_yoy`
   - **Instructions** (optional but recommended): Add context like
     "This data contains Australian retail trade and food price data.
     States are Australian states. Turnover is in millions AUD."

> **Stuck?** Grab **Checkpoint 2B**: step-by-step Genie setup instructions with
> recommended table descriptions and sample questions.

---

## Phase 2: Build Backend + Frontend (25 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Build FastAPI backend using `starter-kit/prompts/08-build-backend.md`
> - **Person B (Terminal):** Build frontend using `starter-kit/prompts/09-build-frontend.md`
> - **Person C (Databricks UI):** Create AI/BI dashboard — this is another UI task. Navigate to Dashboards → Create → AI/BI Dashboard. Use gold tables.
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

> **Starter Kit:** Copy-paste prompts in `starter-kit/prompts/08-build-backend.md` and `09-build-frontend.md`.

### 2.1 Implement the backend

```
Implement the FastAPI backend to pass all tests.

For /api/metrics:
- Query the retail_summary gold table with optional filters
- Use databricks-sql-connector with parameterized queries
- Return results as JSON

For /api/ask:
- Send the user's question to the Foundation Model API with
  the table schema as context
- The LLM generates a SQL query
- Execute the SQL and return results with the generated query

Connection details from environment variables:
- DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN

Run tests after implementation.
```

### 2.2 Build the frontend

**Choose your approach based on your tier:**

#### Option A: Embedded AI/BI Dashboard (Tier 1 — Quick)

```
Build a frontend in static/index.html with:

1. Header: "Grocery Intelligence Platform" with your team name
2. An iframe embedding our published AI/BI dashboard (I'll give you the URL)
3. "Ask AI" section: text input + response area
4. Use Tailwind CSS from CDN
5. Clean, professional styling (dark header, white cards)
```

To get the embed URL:
1. Person C creates and publishes the AI/BI dashboard during this phase (see 2.4 below)
2. Click **Share** → **Embed** → copy the iframe code
3. Paste the `<iframe>` into your app's HTML

#### Option B: Custom Charts with Recharts (Tier 2 — Medium)

```
Build a React frontend with:

1. Header: "Grocery Intelligence Platform" with your team name
2. Filter bar: state dropdown, date range pickers
3. Recharts line chart: monthly retail turnover over time
4. Recharts bar chart: YoY growth by state
5. Metric cards: Total Turnover, Average Growth %, Top State
6. "Ask AI" section: text input + response area
7. Use Tailwind CSS for styling
8. Fetch data from FastAPI endpoints

Install: npm install recharts
```

Alternative: **Observable Plot** if you don't want React:
```
Use Observable Plot (https://observablehq.com/plot/) for charts.
Include via CDN: <script src="https://cdn.jsdelivr.net/npm/@observablehq/plot"></script>
Declarative, D3-based, works with vanilla HTML.
```

#### Option C: Full Platform (Tier 3 — Stretch)

```
Build a React frontend with:

1. Header with team name and navigation tabs
2. Dashboard tab: Recharts/Observable charts + embedded AI/BI iframe
3. Explorer tab: Filter bar + data table with sorting
4. Ask AI tab: NL query with SQL display and result viz
5. Metric cards with sparklines
6. Responsive layout with Tailwind CSS
```

### 2.3 Wire it together

```
Create app.py that:
1. Serves FastAPI with CORS middleware
2. Mounts static files from static/ directory
3. Serves index.html at root
4. Has proper error handling

Create app.yaml for Databricks Apps:
  command: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

Create requirements.txt with all dependencies.

Run all tests one final time.
```

### 2.4 Create AI/BI dashboard (Person C)

AI/BI dashboards are auto-generated visualizations that understand your data. You describe what you want to see in natural language, and the dashboard creates the charts.

In the Databricks workspace UI:

1. Navigate to **Dashboards** in the left sidebar
2. Click **Create Dashboard** → **AI/BI Dashboard**
3. Connect to your gold tables
4. Use natural language to create visualizations:

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

> **Stuck?** Grab **Checkpoint 2C**: pre-written SQL queries for common
> dashboard visualizations you can paste directly.

> **Stuck at 25 minutes?** Grab **Checkpoint 2A**: a working app skeleton with
> health endpoint, database connection, and basic structure. Focus your remaining
> time on Genie + Dashboard.

---

## Phase 3: Wire + Polish (15 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Wire together app.py, deploy to Databricks Apps using `starter-kit/prompts/11-deploy-app.md`
> - **Person B (Databricks UI):** Test Genie space with sample questions, refine instructions
> - **Person C (Databricks UI):** Polish AI/BI dashboard, get embed URL, share with Person A for iframe
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

> **Starter Kit:** Deployment prompt in `starter-kit/prompts/11-deploy-app.md`. App config template at `starter-kit/app.yaml.template`.

### 3.1 Deploy your app

```
Deploy the app to Databricks:

databricks apps deploy --name grocery-app-<team_name> --source-code-path ./

Show me the app URL when it's ready.
```

### 3.2 Test Genie space

Person C should have created your Genie space during Phase 1. Now test it with these questions:

```
Which state had the highest food retail turnover last month?
```

```
Show me the year-over-year food price inflation trend for Victoria.
```

```
Compare retail growth across all states for the last 12 months.
```

> **Tip:** If Genie generates incorrect SQL, add table descriptions and column
> comments in Unity Catalog. The richer the metadata, the better Genie performs.

### 3.3 Polish AI/BI dashboard

Person C should have created the dashboard during Phase 2. Now polish it:

1. Arrange the visualizations into a clean layout
2. Add a title: "Grocery Intelligence Dashboard — Team [your_team]"
3. Click **Publish** on your dashboard
4. Click **Share** → **Embed** → copy the iframe code
5. Share the embed URL with Person A to add to the app:

```html
<div style="width:100%;height:600px;">
  <iframe
    src="YOUR_EMBED_URL_HERE"
    width="100%"
    height="100%"
    frameborder="0"
  ></iframe>
</div>
```

> **Note:** Embedded dashboards display in light mode only. Users need Databricks credentials to view (or use service principal embedding for external users).

### 3.4 Verify everything works

- [ ] App loads in browser with dashboard
- [ ] Filters work (state, date range)
- [ ] "Ask AI" returns meaningful answers
- [ ] Genie space answers natural language questions
- [ ] AI/BI dashboard shows your visualizations

> **Stuck?** Grab **Checkpoint 2B** (Genie setup), **Checkpoint 2C** (dashboard SQL),
> or **Checkpoint 2D** (complete solution).

---

## Phase 4: Demo Prep (5 min)

> **Team Tasks for This Phase**
> - **All:** Prepare demo script, decide who presents what (pipeline, app, Genie, dashboard)
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 4.1 Prepare your demo

You have 3 minutes to show:
1. Your pipeline (quick: show the DAG or table list)
2. Your app (show it running, use the AI feature)
3. Your Genie space (ask it a question live)
4. Your dashboard (show the key visualizations)
5. One thing that surprised you

> **Stuck?** Grab **Checkpoint 2D**: complete solution for reference.

---

## Using MCP During This Lab

MCP servers are available to help you build faster:

**Databricks Docs MCP** — search official documentation:
```
Search the Databricks docs for how to create a Genie space programmatically.
```

**Using skills** — speed up common tasks:
```
/commit    — commit with a good message
/test      — run and fix failing tests
```

**AI Dev Kit skills** — pre-built Databricks patterns:
```
Use the databricks skills to help scaffold the app deployment.
```

---

## Pro Tips

> **Steering the agent effectively:**
>
> - **Divide and conquer:** One person works on the app, another sets up Genie, another does the dashboard
> - If htmx isn't working, check the `<script>` tag: `<script src="https://unpkg.com/htmx.org@2.0.4"></script>`
> - For the AI query feature, include the table schema in the LLM system prompt
> - If the agent writes raw SQL concatenation, say **"parameterize all queries to prevent injection"**
> - Use **`/commit`** regularly to save your progress
> - If the frontend looks wrong, say **"take a screenshot"** or describe what you see
> - **Don't over-engineer** — a working app is better than a perfect app that's not done

---

## Success Criteria

- [ ] FastAPI backend with tested endpoints
- [ ] HTML frontend with Tailwind + htmx
- [ ] AI-powered natural language query feature
- [ ] Genie space created and answering questions
- [ ] AI/BI dashboard with at least 3 visualizations
- [ ] App deployed to Databricks Apps
- [ ] All tests passing
- [ ] Ready for 3-minute demo!

---

## Bonus Challenge: Build an MCP Server for Retail Analytics

**Goal:** Wrap your Retail Analytics App as an MCP server so any AI agent (Claude Code, Cursor, ChatGPT) can query retail trends, food prices, and state comparisons through the MCP protocol.

**Why this matters:** You've been _using_ MCP servers all day. Now you'll _build_ one — the same pattern Coles could use to expose internal data to every agent in the organisation.

### What to build

Your MCP server should expose these tools:

| Tool | Description | Example call |
|------|-------------|-------------|
| `get_retail_turnover` | Monthly retail turnover by state and industry | `get_retail_turnover(state="NSW", months=12)` |
| `get_food_inflation` | Year-over-year food CPI changes by category | `get_food_inflation(category="Dairy", since="2020-01")` |
| `compare_states` | Side-by-side comparison of two states | `compare_states(state_a="VIC", state_b="QLD")` |
| `get_top_insights` | Auto-generated summary of notable trends | `get_top_insights(limit=5)` |

### How to build it

Ask Claude to help you:

```
Build an MCP server that wraps our Retail Analytics API.
Use the FastMCP Python library. Expose 4 tools:
- get_retail_turnover: query retail_summary gold table
- get_food_inflation: query food_inflation_yoy gold table
- compare_states: compare two states side-by-side
- get_top_insights: return the most notable trends

Connect to Unity Catalog via databricks-sql-connector.
Return structured JSON from each tool.
```

### Test it

```bash
# Run locally first
uv run python mcp_server.py

# Test with MCP Inspector
npx @modelcontextprotocol/inspector python mcp_server.py

# Or connect from Claude Code settings:
# "mcpServers": { "retail": { "command": "python", "args": ["mcp_server.py"] } }
```

### Deploy to Databricks Apps (stretch)

```bash
databricks apps deploy --name "retail-mcp-${TEAM}" --source-code-path ./mcp-server/
```

Now any agent in the org can query Coles retail data via MCP — no custom integration code.

---

## Other Bonus Challenges (if time permits)

1. **Add charts:** Use Chart.js (CDN) to add a revenue trend line chart to your app
2. **Add FSANZ data:** If you included food recalls in your pipeline, add a recalls feed to the app
3. **Custom skill:** Create a `/deploy` skill that bundles validate + deploy in one command
4. **Cross-team Genie:** Add another team's gold tables to your Genie space for richer queries

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **htmx not loading** | Check `<script src="https://unpkg.com/htmx.org@2.0.4"></script>` is in `<head>`. Check browser DevTools console. |
| **CORS errors** | Add `CORSMiddleware` to FastAPI with `allow_origins=["*"]`. The agent sometimes forgets this. |
| **AI generates invalid SQL** | Add the full table schema + column descriptions to the LLM system prompt. Include 2-3 example queries. |
| **Can't create Genie space** | Check permissions: you need CREATE GENIE SPACE on the catalog. Ask David for help. |
| **Dashboard queries are slow** | Gold tables are materialized views — they should be fast. Check your SQL warehouse is running. |
| **App deploys but shows blank page** | Check static files are mounted: `app.mount("/static", StaticFiles(directory="static"))`. Check Databricks App logs. |
| **databricks-sql-connector errors** | Ensure it's in requirements.txt. Check DATABRICKS_HOST, DATABRICKS_HTTP_PATH, DATABRICKS_TOKEN env vars. |
| **Running out of time** | Prioritize: working app > Genie > dashboard. Grab checkpoints for what you can't finish. |

---

## Reflection Questions (for Demo)

1. How did the PRD guide the agent's decisions?
2. How does Genie compare to your custom AI query feature?
3. What would you need to add to make this production-ready?
4. Which approach (app vs. Genie vs. AI/BI dashboard) is most useful for your team?
