"""
Fast local tests for DS track — model training & evaluation logic.
Runs WITHOUT Spark, Databricks, or MLflow server.
Uses sklearn and xgboost directly on small numpy/pandas data.

Pattern: test model behavior on synthetic data locally,
then run on real feature table when on the cluster.

Run: uv run pytest tests/test_model_local.py -x --no-header -q
"""
import pytest
import numpy as np
from datetime import date


# ── Synthetic feature data (mimics retail_features table) ─────────


def make_synthetic_features(n_months: int = 36, seed: int = 42) -> tuple:
    """
    Generate synthetic retail turnover data with known patterns.
    Returns (X, y, dates) — numpy arrays ready for sklearn.

    Patterns embedded:
    - Seasonal: December spike, January dip
    - Trend: 2% annual growth
    - Noise: small random variation
    """
    rng = np.random.default_rng(seed)
    dates = []
    features = []
    targets = []

    base_turnover = 4000.0
    for i in range(n_months):
        month_num = (i % 12) + 1
        year_offset = i // 12

        # Base with trend
        turnover = base_turnover * (1 + 0.02 * year_offset)

        # Seasonal pattern
        if month_num == 12:
            turnover *= 1.15  # December spike
        elif month_num == 1:
            turnover *= 0.92  # January dip
        elif month_num in [6, 7]:
            turnover *= 0.95  # Winter dip (Australia)

        # Add noise
        turnover += rng.normal(0, 50)

        # Build feature vector
        lag_1m = targets[-1] if i > 0 else None
        lag_3m = targets[-3] if i >= 3 else None
        lag_6m = targets[-6] if i >= 6 else None
        lag_12m = targets[-12] if i >= 12 else None
        quarter = (month_num - 1) // 3 + 1

        if lag_1m is not None and lag_12m is not None:
            mom_growth = ((turnover - lag_1m) / lag_1m) * 100
            yoy_growth = ((turnover - lag_12m) / lag_12m) * 100
            features.append([
                lag_1m, lag_3m or 0, lag_6m or 0, lag_12m,
                month_num, quarter,
                1.0 if month_num == 12 else 0.0,
                1.0 if quarter == 4 else 0.0,
                mom_growth, yoy_growth,
            ])
            targets.append(turnover)
            dates.append(date(2022 + year_offset, month_num, 1))
        else:
            targets.append(turnover)

    X = np.array(features)
    y = np.array(targets[len(targets) - len(features):])
    return X, y, dates


FEATURE_NAMES = [
    "turnover_lag_1m", "turnover_lag_3m", "turnover_lag_6m", "turnover_lag_12m",
    "month_of_year", "quarter", "is_december", "is_q4",
    "turnover_mom_growth", "turnover_yoy_growth",
]


# ── Fixtures ─────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def synthetic_data():
    """36 months of synthetic retail data."""
    return make_synthetic_features(n_months=36)


@pytest.fixture(scope="module")
def train_test_split(synthetic_data):
    """80/20 chronological split (not random — time series!)."""
    X, y, dates = synthetic_data
    split_idx = int(len(X) * 0.8)
    return {
        "X_train": X[:split_idx],
        "y_train": y[:split_idx],
        "X_test": X[split_idx:],
        "y_test": y[split_idx:],
        "dates_test": dates[split_idx:],
    }


# ── Tests: Data Preparation ──────────────────────────────────────


class TestDataPreparation:
    """Verify synthetic data has the right shape for training."""

    def test_feature_count(self, synthetic_data):
        X, y, _ = synthetic_data
        assert X.shape[1] == len(FEATURE_NAMES)

    def test_no_nans_in_features(self, synthetic_data):
        X, y, _ = synthetic_data
        assert not np.any(np.isnan(X)), "Features should have no NaN after filtering"

    def test_target_all_positive(self, synthetic_data):
        _, y, _ = synthetic_data
        assert np.all(y > 0), "Turnover must be positive"

    def test_chronological_split(self, train_test_split):
        """Train set is before test set — no data leakage."""
        data = train_test_split
        assert len(data["X_train"]) > len(data["X_test"])
        # Test dates should be after training period
        assert data["dates_test"][0] > date(2023, 1, 1)


# ── Tests: RandomForest Model ────────────────────────────────────


class TestRandomForestModel:
    """Test sklearn RandomForestRegressor on synthetic data."""

    @pytest.fixture(scope="class")
    def rf_model(self, train_test_split):
        from sklearn.ensemble import RandomForestRegressor
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(train_test_split["X_train"], train_test_split["y_train"])
        return model

    def test_predictions_positive(self, rf_model, train_test_split):
        """All predictions must be positive (turnover can't be negative)."""
        predictions = rf_model.predict(train_test_split["X_test"])
        assert np.all(predictions > 0), "RandomForest produced negative predictions"

    def test_r2_score_above_threshold(self, rf_model, train_test_split):
        """R² > 0.5 on test set."""
        from sklearn.metrics import r2_score
        data = train_test_split
        predictions = rf_model.predict(data["X_test"])
        r2 = r2_score(data["y_test"], predictions)
        assert r2 > 0.5, f"R² = {r2:.3f}, expected > 0.5"

    def test_predictions_in_reasonable_range(self, rf_model, train_test_split):
        """Predictions should be within realistic turnover range."""
        predictions = rf_model.predict(train_test_split["X_test"])
        assert np.all(predictions > 1000), "Predictions too low for retail turnover"
        assert np.all(predictions < 10000), "Predictions unrealistically high"

    def test_feature_importances_exist(self, rf_model):
        """RandomForest provides feature importances."""
        importances = rf_model.feature_importances_
        assert len(importances) == len(FEATURE_NAMES)
        assert np.sum(importances) == pytest.approx(1.0, abs=0.01)


# ── Tests: XGBoost Model ─────────────────────────────────────────


class TestXGBoostModel:
    """Test XGBRegressor on synthetic data."""

    @pytest.fixture(scope="class")
    def xgb_model(self, train_test_split):
        from xgboost import XGBRegressor
        model = XGBRegressor(n_estimators=50, max_depth=4, random_state=42)
        model.fit(train_test_split["X_train"], train_test_split["y_train"])
        return model

    def test_predictions_positive(self, xgb_model, train_test_split):
        """All predictions must be positive."""
        predictions = xgb_model.predict(train_test_split["X_test"])
        assert np.all(predictions > 0), "XGBoost produced negative predictions"

    def test_r2_score_above_threshold(self, xgb_model, train_test_split):
        """R² > 0.5 on test set."""
        from sklearn.metrics import r2_score
        data = train_test_split
        predictions = xgb_model.predict(data["X_test"])
        r2 = r2_score(data["y_test"], predictions)
        assert r2 > 0.5, f"R² = {r2:.3f}, expected > 0.5"

    def test_mae_reasonable(self, xgb_model, train_test_split):
        """Mean Absolute Error should be < 10% of mean turnover."""
        from sklearn.metrics import mean_absolute_error
        data = train_test_split
        predictions = xgb_model.predict(data["X_test"])
        mae = mean_absolute_error(data["y_test"], predictions)
        mean_turnover = np.mean(data["y_test"])
        assert mae < mean_turnover * 0.1, f"MAE={mae:.1f} > 10% of mean={mean_turnover:.1f}"


# ── Tests: Model Comparison ──────────────────────────────────────


class TestModelComparison:
    """Compare RandomForest vs XGBoost — the pattern teams follow in Lab 2."""

    @pytest.fixture(scope="class")
    def both_models(self, train_test_split):
        from sklearn.ensemble import RandomForestRegressor
        from xgboost import XGBRegressor
        from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

        data = train_test_split

        rf = RandomForestRegressor(n_estimators=50, random_state=42)
        rf.fit(data["X_train"], data["y_train"])
        rf_pred = rf.predict(data["X_test"])

        xgb = XGBRegressor(n_estimators=50, max_depth=4, random_state=42)
        xgb.fit(data["X_train"], data["y_train"])
        xgb_pred = xgb.predict(data["X_test"])

        return {
            "rf": {
                "model": rf,
                "predictions": rf_pred,
                "r2": r2_score(data["y_test"], rf_pred),
                "mae": mean_absolute_error(data["y_test"], rf_pred),
                "rmse": np.sqrt(mean_squared_error(data["y_test"], rf_pred)),
            },
            "xgb": {
                "model": xgb,
                "predictions": xgb_pred,
                "r2": r2_score(data["y_test"], xgb_pred),
                "mae": mean_absolute_error(data["y_test"], xgb_pred),
                "rmse": np.sqrt(mean_squared_error(data["y_test"], xgb_pred)),
            },
        }

    def test_both_models_beat_baseline(self, both_models):
        """Both models should beat R² = 0 (predicting the mean)."""
        assert both_models["rf"]["r2"] > 0, "RandomForest worse than mean predictor"
        assert both_models["xgb"]["r2"] > 0, "XGBoost worse than mean predictor"

    def test_metrics_are_logged(self, both_models):
        """Both models produce the three metrics we log to MLflow."""
        for name in ["rf", "xgb"]:
            metrics = both_models[name]
            assert "r2" in metrics
            assert "mae" in metrics
            assert "rmse" in metrics
            assert metrics["rmse"] >= metrics["mae"], "RMSE should be >= MAE"


# ── Tests: MLflow Logging Pattern (no server needed) ─────────────


class TestMLflowLoggingPattern:
    """
    Test that MLflow API calls work locally (uses local file store).
    Teams use the same pattern on the cluster with a Databricks-backed store.
    """

    def test_mlflow_log_metrics(self, train_test_split):
        """Verify we can log the metrics MLflow expects."""
        import mlflow
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import r2_score, mean_absolute_error

        data = train_test_split
        model = RandomForestRegressor(n_estimators=10, random_state=42)
        model.fit(data["X_train"], data["y_train"])
        preds = model.predict(data["X_test"])

        with mlflow.start_run(run_name="local-test-run"):
            mlflow.log_param("model_type", "RandomForest")
            mlflow.log_param("n_estimators", 10)
            mlflow.log_metric("r2", r2_score(data["y_test"], preds))
            mlflow.log_metric("mae", mean_absolute_error(data["y_test"], preds))
            mlflow.sklearn.log_model(model, "model")

            run = mlflow.active_run()
            assert run is not None
            assert run.info.run_name == "local-test-run"

    def test_mlflow_autolog(self, train_test_split):
        """Verify sklearn autolog works locally."""
        import mlflow
        from sklearn.ensemble import RandomForestRegressor

        mlflow.sklearn.autolog(log_models=False)
        data = train_test_split

        with mlflow.start_run(run_name="autolog-test"):
            model = RandomForestRegressor(n_estimators=10, random_state=42)
            model.fit(data["X_train"], data["y_train"])
            model.score(data["X_test"], data["y_test"])

        mlflow.sklearn.autolog(disable=True)
