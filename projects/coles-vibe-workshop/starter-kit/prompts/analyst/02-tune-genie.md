## Step 2: Tune Genie with Metadata

Adding column descriptions and table comments dramatically improves Genie accuracy.

### Prompt

Paste this into Claude Code:

```
Add column comments to our gold tables for better Genie and AI/BI accuracy:

For workshop_vibe_coding.TEAM_SCHEMA.retail_summary:
- Table comment: "Monthly retail turnover summary by Australian state and industry with rolling averages and YoY growth"
- state: "Australian state name (New South Wales, Victoria, Queensland, etc.)"
- industry: "Retail industry category (Food retailing, Department stores, etc.)"
- month: "Date of the monthly observation (first of month)"
- turnover_millions: "Monthly retail turnover in millions of AUD"
- turnover_3m_avg: "3-month rolling average of turnover in millions AUD"
- turnover_12m_avg: "12-month rolling average of turnover in millions AUD"
- yoy_growth_pct: "Year-over-year turnover growth as a percentage"

For workshop_vibe_coding.TEAM_SCHEMA.food_inflation_yoy:
- Table comment: "Quarterly food price inflation by Australian state with YoY CPI changes"
- state: "Australian state name"
- quarter: "Calendar quarter (e.g., 2024-Q1)"
- cpi_index: "Consumer Price Index value (base period = 100)"
- yoy_change_pct: "Year-over-year CPI change as a percentage (positive = inflation)"

Use ALTER TABLE ... SET TBLPROPERTIES for table comments.
Use ALTER TABLE ... ALTER COLUMN ... COMMENT for column comments.
```

### Expected Result

Both tables have descriptive comments visible in Unity Catalog. Genie should now give better answers.

### If It Doesn't Work

- **Permission denied:** You need ALTER permission on the tables. Ask the facilitator.
- **ALTER COLUMN syntax error:** Use: `ALTER TABLE t ALTER COLUMN c COMMENT 'description'`
