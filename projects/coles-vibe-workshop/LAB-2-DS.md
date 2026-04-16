# Lab 2: Model Training, Serving & App (Data Science Track)

**Duration:** 55 minutes
**Goal:** Train a forecasting model, register in MLflow, serve via Model Serving, build a prediction app
**Team Size:** 2–3 people

> Complete `LAB-0-GETTING-STARTED.md` and `LAB-1-DS.md` first.

---

## The Mission

Your feature table is ready. Train a model to predict retail turnover, register it in MLflow, serve it as an endpoint, and build a simple web app that calls it.

---

## Phase 1: Train Model + Write Tests (15 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Write tests for model training (input schema, positive predictions, R² > 0.5)
> - **Person B (Terminal):** Implement training script — read features, train model, log to MLflow
> - **Person C (Databricks UI):** Verify Model Serving permissions, check Model Registry is accessible
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 1.1 Write model tests

```
Write pytest tests for model training in tests/test_model.py:

1. test_model_predictions_positive: all predictions are positive (turnover can't be negative)
2. test_model_r2_score: R² > 0.5 on test set
3. test_model_logged_to_mlflow: run has model artifact, R², MAE, RMSE metrics

Write ONLY tests. Do NOT implement yet.
```

### 1.2 Train the model

```
Train a retail turnover forecasting model:

1. Read feature table: workshop_vibe_coding.TEAM_SCHEMA.retail_features
2. Target: turnover_millions
3. Features: all lag, seasonal, and growth columns
4. Split: 80% train / 20% test (split by date, not random)
5. Try both RandomForestRegressor and XGBRegressor
6. Use mlflow.sklearn.autolog() or mlflow.xgboost.autolog()
7. Log both models, compare R², MAE, RMSE
8. Print which model performed better

Run tests after training.
```

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/ds/04-train-model.md`

---

## Phase 2: Register + Serve (20 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Register best model in MLflow Model Registry
> - **Person B (Terminal):** Create Model Serving endpoint, test with sample request
> - **Person C (Terminal):** Write tests for serving endpoint response schema
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 2.1 Register the model

```
Register the best model from our experiment:

1. Find the best run (highest R²) from our MLflow experiment
2. Register as: workshop_vibe_coding.TEAM_SCHEMA.retail_forecast_model
3. Add description: "Retail turnover forecasting model for Australian states"
4. Set alias "production" on the latest version
```

### 2.2 Create serving endpoint

```
Create a Model Serving endpoint:

1. Name: grocery-forecast-TEAM_NAME
2. Model: workshop_vibe_coding.TEAM_SCHEMA.retail_forecast_model (production alias)
3. Serverless endpoint
4. Wait for it to be ready (may take 5-10 minutes)
5. Test with a sample request:
   {"dataframe_records": [{"turnover_lag_1m": 4500, "turnover_lag_3m": 4400, "turnover_lag_12m": 4200, "month_of_year": 3, "quarter": 1, "is_december": false, "is_q4": false, "turnover_mom_growth": 2.3, "turnover_yoy_growth": 7.1}]}

Show me the prediction response.
```

> **Starter Kit:** Copy-paste prompts in `starter-kit/prompts/ds/05-register-model.md` and `ds/06-serve-model.md`

> **Stuck at 25 minutes?** Grab **Checkpoint DS-2B**: pre-registered model + working endpoint.

---

## Phase 3: Build Prediction App (15 min)

> **Team Tasks for This Phase**
> - **Person A (Terminal):** Build FastAPI backend with `/predict` endpoint calling Model Serving
> - **Person B (Terminal):** Build HTML + Tailwind frontend with prediction form
> - **Person C (Databricks UI):** Test end-to-end flow, verify predictions make sense
>
> *Teams of 2: Person A takes Terminal tasks, Person B takes Terminal + UI tasks.*

### 3.1 Build the app

```
Build a prediction web app:

1. FastAPI backend (app/app.py):
   - GET /health → {"status": "ok"}
   - POST /predict:
     Accepts: {"state": "New South Wales", "industry": "Food retailing", "month": "2024-06"}
     Looks up latest features for that state/industry from the feature table
     Calls our Model Serving endpoint
     Returns: {"predicted_turnover": 4650.2, "state": "New South Wales", "industry": "Food retailing"}
   - GET / → serves the frontend

2. Frontend (app/static/index.html):
   - Tailwind CSS + htmx (CDN, no build step)
   - Header: "Grocery Forecast — TEAM_NAME"
   - Form: dropdowns for State, Industry, Month
   - Submit → calls POST /predict → shows result card
   - Keep it simple and clean

3. Create app/app.yaml and app/requirements.txt
4. Deploy: databricks apps deploy --name grocery-forecast-TEAM_NAME --source-code-path ./app/
```

> **Starter Kit:** Copy-paste prompt in `starter-kit/prompts/ds/07-build-app.md`

---

## Phase 4: Demo Prep (5 min)

You have 3 minutes to show:
1. Your feature table (show in UC browser)
2. Your MLflow experiment (show runs, metrics, artifacts)
3. Your model (show registry + serving endpoint)
4. Your app (make a prediction live)
5. One thing that surprised you

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **Model training OOM** | Reduce feature count or sample size. Collect to pandas for small datasets. |
| **Model Serving 404** | Endpoint takes 5-10 min to provision. Check status in UI or `databricks serving-endpoints get`. |
| **Model Serving auth error** | Check `DATABRICKS_TOKEN` env var is set. |
| **App can't reach endpoint** | Use workspace-internal URL, not external. |
| **Low R² score** | Try XGBoost instead of RandomForest, or add more features. |
| **Model Registry permission error** | Check CREATE MODEL permission on catalog. Ask facilitator. |
| **mlflow.register_model fails** | Use full UC path: `models:/workshop_vibe_coding.TEAM_SCHEMA.model_name` |
| **Running out of time** | Grab checkpoint DS-2C (complete app) or DS-2D (complete solution). |

---

## Success Criteria

- [ ] Model trained with R² > 0.5
- [ ] Model registered in Unity Catalog Model Registry
- [ ] Model Serving endpoint responding to requests
- [ ] Prediction app deployed to Databricks Apps
- [ ] End-to-end flow: form → API → Model Serving → response
- [ ] All tests passing
- [ ] Ready for 3-minute demo

---

## Reflection Questions (for Demo)

1. How accurate were your model's predictions?
2. What was the hardest part — training, serving, or building the app?
3. How would you improve the model for production use?
4. How does MLflow help with model lifecycle management?
