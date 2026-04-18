## Step 5: Add FSANZ Food Recalls Data Source

### Prompt

```
Add a new data source to our pipeline — FSANZ food recalls.

1. Write tests first:
   - test_bronze_food_recalls_schema: has columns (product, category, issue, date, state, url)
   - test_bronze_food_recalls_not_null: product and date are never null
   - test_silver_food_recalls_dates: date strings parsed to proper DATE type
   - test_silver_food_recalls_states: state names normalized to match our existing state list

2. Build bronze + silver tables:
   - src/bronze/fsanz_food_recalls.py: @dp.table ingesting from FSANZ
   - src/silver/food_recalls.py: @dp.table with cleaned dates, normalized states, categorized issues
   - Data source: https://www.foodstandards.gov.au/food-recalls/recalls
   - If website is blocked, read from: workshop_vibe_coding.checkpoints.fsanz_food_recalls

3. Run tests after implementation.
```

### Expected Result

Two new pipeline files and passing tests for the FSANZ data source.

### If It Doesn't Work

- **Website blocked:** Use checkpoint data: `spark.read.table("workshop_vibe_coding.checkpoints.fsanz_food_recalls")`
- **Scraping errors:** Try the RSS feed: `https://www.foodstandards.gov.au/rss/recalls`
- **State names don't match:** Map to the same state names used in retail_summary
