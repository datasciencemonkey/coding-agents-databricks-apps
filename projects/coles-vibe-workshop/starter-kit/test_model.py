"""
Model training and serving test stubs for Data Science track Lab 2.
Copy to tests/test_model.py before starting.
"""


# ── Model Training ────────────────────────────────────────────────────


def test_model_predictions_positive(spark):
    """All predictions are positive numbers (turnover can't be negative)."""
    # TODO: Load model, run predictions on test set
    # TODO: Assert all predictions > 0
    pass


def test_model_r2_score(spark):
    """Model achieves R² > 0.5 on test set."""
    # TODO: Load model, predict on held-out test data
    # TODO: Calculate R² score
    # TODO: Assert R² > 0.5
    pass


def test_model_logged_to_mlflow():
    """Training run logged model artifact to MLflow."""
    # TODO: Query MLflow for latest run in our experiment
    # TODO: Assert run has a logged model artifact
    # TODO: Assert run has R², MAE, RMSE metrics logged
    pass


# ── Model Serving ─────────────────────────────────────────────────────


def test_serving_endpoint_health():
    """Model Serving endpoint responds to health check."""
    # TODO: Query serving endpoint status
    # TODO: Assert endpoint state is "READY"
    pass


def test_serving_endpoint_prediction():
    """Model Serving endpoint returns valid predictions."""
    # TODO: Send sample feature vector to endpoint
    # TODO: Assert response has predictions key
    # TODO: Assert prediction is a positive number
    pass
