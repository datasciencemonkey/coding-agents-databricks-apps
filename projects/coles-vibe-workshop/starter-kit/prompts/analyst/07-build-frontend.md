## Step 9: Build the Frontend

HTML + Tailwind + htmx — no build step required.

### Prompt

Paste this into Claude Code:

```
Build the frontend in app/static/index.html:

1. Include these CDN scripts in <head>:
   - Tailwind CSS: <script src="https://cdn.tailwindcss.com"></script>
   - htmx: <script src="https://unpkg.com/htmx.org@2.0.4"></script>

2. Layout:
   - Dark header bar: "Grocery Intelligence Platform — TEAM_NAME"
   - Three metric cards at the top: Total Turnover, Average Growth %, Top State
     (fetch from GET /api/metrics on page load)
   - Filter bar: State dropdown, date range pickers
   - Data table showing metrics (updated via htmx when filters change)
   - "Ask AI" section at the bottom:
     - Text input for questions
     - Submit button
     - Response area showing the answer and the generated SQL

3. Use htmx for all dynamic updates:
   - hx-get="/api/metrics" for the data table
   - hx-post="/api/ask" for the AI question
   - hx-trigger="change" on filters to auto-refresh

4. Style with Tailwind:
   - Clean, professional look
   - White cards with subtle shadows
   - Responsive layout

Also update app/app.py to:
- Mount static files: app.mount("/static", StaticFiles(directory="static"))
- Serve index.html at GET /
- Add CORSMiddleware with allow_origins=["*"]
```

### Expected Result

A single `app/static/index.html` file. When you run `uvicorn app.app:app`, the page loads with the dashboard.

### If It Doesn't Work

- **Blank page:** Check browser DevTools console (F12) for errors. Usually a missing script tag.
- **htmx not working:** Make sure the script tag is in `<head>`, not `<body>`.
- **CORS errors:** Add CORSMiddleware to FastAPI (the agent sometimes forgets this).
- **Static files not serving:** Check `app.mount("/static", StaticFiles(directory="static"))` in app.py.
