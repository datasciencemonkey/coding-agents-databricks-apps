## Step 4: Train the Model

### Prompt

```
Train a retail turnover forecasting model:

1. Write tests first:
   - test_model_predictions_positive: all predictions are positive
   - test_model_r2_score: R² > 0.5 on test set
   - test_model_logged_to_mlflow: run has model artifact and metrics

2. Implement training:
   - Read feature table: workshop_vibe_coding.TEAM_SCHEMA.retail_features
   - Target: turnover_millions
   - Features: all lag, seasonal, and growth columns
   - Split: 80% train / 20% test (split by date, not random)
   - Try both RandomForestRegressor and XGBRegressor
   - Use mlflow.sklearn.autolog() or mlflow.xgboost.autolog()
   - Log both models, compare R², MAE, RMSE
   - Print which model performed better

Run tests after training.
```

### Expected Result

Two models logged to MLflow. One should have R² > 0.5. Tests pass.

### If It Doesn't Work

- **XGBoost not installed:** `pip install xgboost`
- **Low R² score:** Try adding more features or using a different split ratio
- **OOM error:** Collect to pandas for training (sklearn needs pandas/numpy, not Spark)
