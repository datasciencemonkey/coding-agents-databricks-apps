## Step 3: Build AI/BI Dashboard

This is done in the Databricks UI, not the terminal.

### Steps

1. Navigate to **Dashboards** in the left sidebar
2. Click **Create Dashboard** → **AI/BI Dashboard**
3. Connect to your gold tables:
   - `workshop_vibe_coding.TEAM_SCHEMA.retail_summary`
   - `workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy`

4. Create visualizations using natural language:

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

5. Arrange visualizations into a clean layout
6. Add a title: "Grocery Intelligence Dashboard — TEAM_NAME"
7. Click **Publish**

### Expected Result

A published dashboard with 4-5 visualizations accessible via URL.

### If It Doesn't Work

- **Dashboard viz doesn't match prompt:** Try rephrasing. Be specific about chart type and time range.
- **"No data" message:** Check the SQL warehouse is running (Compute → SQL Warehouses).
- **Can't connect to tables:** Verify table names match exactly including schema.
- **Want custom SQL:** Click the SQL icon on any viz to write your own query.
