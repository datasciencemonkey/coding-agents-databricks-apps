## Step 3: Track Experiments with MLflow

### Prompt

```
Set up MLflow experiment tracking for our feature engineering:

1. Create an MLflow experiment named "grocery-features-TEAM_NAME"

2. Log a run with:
   - Parameters: number of features, date range, number of states
   - Metrics: feature table row count, null percentage per feature, feature correlation stats
   - Tags: team_name, track="data_science", phase="feature_engineering"
   - Artifacts: save a feature summary CSV showing feature stats per state

3. Create and log a visualization:
   - A correlation heatmap of the numeric features (save as PNG)
   - A time series plot of turnover trends for top 3 states (save as PNG)

Use mlflow.log_param(), mlflow.log_metric(), mlflow.log_artifact().
Show me the MLflow experiment URL when done.
```

### Expected Result

An MLflow experiment with logged parameters, metrics, and artifact visualizations.

### If It Doesn't Work

- **MLflow not found:** Run `pip install mlflow`
- **Experiment URL not showing:** Set explicitly: `mlflow.set_experiment("/Users/.../grocery-features-TEAM_NAME")`
- **Visualization errors:** Use matplotlib. `pip install matplotlib seaborn` if needed.
