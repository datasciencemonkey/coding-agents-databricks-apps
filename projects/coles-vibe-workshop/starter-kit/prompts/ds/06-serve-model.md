## Step 6: Create Model Serving Endpoint

### Prompt

```
Create a Model Serving endpoint for our registered model:

1. Create a serverless endpoint:
   - Name: grocery-forecast-TEAM_NAME
   - Model: workshop_vibe_coding.TEAM_SCHEMA.retail_forecast_model
   - Version: the one with alias "production"
   - Use the Databricks SDK or CLI

2. Wait for the endpoint to be ready (may take 5-10 minutes)

3. Test with a sample request:
   POST /serving-endpoints/grocery-forecast-TEAM_NAME/invocations
   Body: {"dataframe_records": [{"turnover_lag_1m": 4500, "turnover_lag_3m": 4400, "turnover_lag_12m": 4200, "month_of_year": 3, "quarter": 1, "is_december": false, "is_q4": false, "turnover_mom_growth": 2.3, "turnover_yoy_growth": 7.1}]}

Show me the prediction response.
```

### Expected Result

Endpoint status is "READY" and returns a prediction for the sample input.

### If It Doesn't Work

- **Endpoint not ready:** Wait 5-10 minutes. Check status: `databricks serving-endpoints get grocery-forecast-TEAM_NAME`
- **Permission error:** Need CREATE_SERVING_ENDPOINT permission. Ask facilitator.
- **Invalid input:** Ensure feature names match exactly what the model was trained on.
