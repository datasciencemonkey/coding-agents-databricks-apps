## Step 7: Add Pipeline Scheduling

### Prompt

```
Set up automated scheduling for our pipeline:

1. Update databricks.yml to add a cron trigger:
   trigger:
     cron:
       quartz_cron_expression: "0 0 6 * * ?"
       timezone_id: "Australia/Sydney"

2. Validate the bundle: databricks bundle validate
3. Deploy: databricks bundle deploy -t dev
4. Show me the pipeline schedule in the Workflows UI.
```

### Expected Result

Pipeline is scheduled to run at 6 AM Sydney time daily. Visible in the Workflows tab.

### If It Doesn't Work

- **Cron syntax error:** Use Quartz format, not standard cron. The `?` is required for day-of-week.
- **Timezone not found:** Use `Australia/Sydney`, not `AEST`.
- **Pipeline runs but fails:** Check individual table errors in the pipeline UI.
