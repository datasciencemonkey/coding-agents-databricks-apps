## Step 5: Deploy Pipeline with DABs

Package and deploy your pipeline as a Databricks Asset Bundle.

### Prompt

Paste this into Claude Code:

```
Set up Databricks Asset Bundles deployment for our pipeline.

1. Update databricks.yml with:
   - Bundle name: grocery-intelligence-TEAM_NAME
   - Pipeline resource pointing to all our src/ notebooks
   - Serverless: true
   - Catalog: workshop_vibe_coding
   - Schema: TEAM_SCHEMA
   - Dev target as default

2. Validate the bundle:
   databricks bundle validate

3. Deploy to dev:
   databricks bundle deploy -t dev

4. Run the pipeline:
   databricks bundle run grocery-intelligence-TEAM_NAME -t dev

Show me the output of each command.
```

### Expected Result

- `databricks bundle validate` shows no errors
- `databricks bundle deploy` deploys successfully
- Pipeline starts running in the Databricks workspace

### If It Doesn't Work

- **Validate fails:** Check `databricks.yml` syntax. Compare with `starter-kit/databricks.yml.template`.
- **Auth errors:** Run `databricks auth status` to check your token is valid.
- **Pipeline fails on run:** Open the pipeline in the Databricks UI (Workflows tab) to see detailed error logs.
- **Can't find notebooks:** Make sure `src/` paths in databricks.yml match your actual file locations.
