## Step 5: Register Model in MLflow

### Prompt

```
Register the best model from our experiment:

1. Find the best run (highest R²) from our MLflow experiment
2. Register it as a Unity Catalog model:
   - Model name: workshop_vibe_coding.TEAM_SCHEMA.retail_forecast_model
   - Use mlflow.register_model() with the UC path
3. Add a model description: "Retail turnover forecasting model for Australian states"
4. Set an alias "production" on the latest version

Show me the model in the Model Registry UI.
```

### Expected Result

Model registered in Unity Catalog with "production" alias set.

### If It Doesn't Work

- **Permission error:** Need CREATE MODEL on catalog. Ask facilitator.
- **Path format:** Use `models:/workshop_vibe_coding.TEAM_SCHEMA.retail_forecast_model`
- **Version not found:** Check that the run has a logged model artifact first.
