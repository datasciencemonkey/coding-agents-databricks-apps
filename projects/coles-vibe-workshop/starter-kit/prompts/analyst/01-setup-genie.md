## Step 10: Create a Genie Space

This is done in the Databricks UI (not the terminal). Genie lets business users ask questions in plain English.

### Steps

1. Open your Databricks workspace in the browser
2. Click **Genie** in the left sidebar
3. Click **New Genie Space**
4. Configure:
   - **Name:** `Grocery Intelligence — TEAM_NAME`
   - **SQL Warehouse:** Select the workshop SQL warehouse
   - **Tables:** Click "Add tables" and add:
     - `workshop_vibe_coding.TEAM_SCHEMA.retail_summary`
     - `workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy`
   - **General Instructions** (paste this):
     ```
     This data contains Australian retail trade and food price data.
     States are Australian states (New South Wales, Victoria, Queensland, etc.).
     Turnover is in millions of AUD.
     CPI index values are relative to a base period.
     YoY growth and change percentages show year-over-year comparisons.
     ```
5. Click **Save**

### Test Your Genie Space

Try these questions:

```
Which state had the highest food retail turnover last month?
```

```
Show me the year-over-year food price inflation trend for Victoria.
```

```
Compare retail growth across all states for the last 12 months.
```

### If It Doesn't Work

- **Can't find Genie in sidebar:** Ask the facilitator — Genie may need to be enabled for your workspace.
- **"No permission" error:** You need CREATE GENIE SPACE permission on the catalog. Ask the facilitator.
- **Wrong answers:** Add column descriptions to your tables in Unity Catalog. Richer metadata = better Genie answers.
