## Track: Data Science

### Data Source
- Read from gold tables: `workshop_vibe_coding.TEAM_SCHEMA.retail_summary` and `food_inflation_yoy`
- These are pre-loaded in checkpoints — no need to build the pipeline

### Feature Engineering
- Use PySpark for all feature transformations
- Create lag features (1, 3, 6, 12 month lags) using Window functions
- Create seasonal indicators (month_of_year, quarter, is_december)
- Create growth rate features (MoM, YoY)
- Output a feature table in Unity Catalog

### MLflow
- Track experiments with `mlflow.start_run()`
- Log parameters, metrics, and artifacts
- Use `mlflow.sklearn` or `mlflow.xgboost` autologging where possible
- Register best model in Unity Catalog: `mlflow.register_model()`

### Model Serving
- Use Databricks Model Serving (serverless)
- Endpoint accepts JSON input, returns predictions
- Test with `databricks api post /serving-endpoints/{name}/invocations`

### ML Libraries
- scikit-learn for baseline models
- XGBoost for boosted tree models
- pandas is OK for small feature DataFrames after collecting from Spark
- Always start with PySpark for data loading and feature engineering
