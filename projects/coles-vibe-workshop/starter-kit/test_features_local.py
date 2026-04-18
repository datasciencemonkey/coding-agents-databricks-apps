"""
Fast local tests for DS track — feature engineering logic.
Runs WITHOUT Spark or Java. Tests the MATH, not the DataFrame wiring.

Pattern: extract feature logic into pure Python functions,
test them in sub-second, then wire into PySpark Window functions on the cluster.

Run: uv run pytest tests/test_features_local.py -x --no-header -q
"""
import pytest
from datetime import date


# ── Pure Python feature functions (teams implement these) ─────────


def create_lag_features(values: list[float], lag: int) -> list[float | None]:
    """
    Create lag features from a time-ordered list of values.
    Returns a list where element i = values[i - lag], or None if i < lag.
    """
    result = []
    for i in range(len(values)):
        if i < lag:
            result.append(None)
        else:
            result.append(values[i - lag])
    return result


def extract_seasonal_features(d: date) -> dict:
    """
    Extract seasonal indicators from a date.
    Returns month_of_year, quarter, is_december, is_q4.
    """
    month = d.month
    quarter = (month - 1) // 3 + 1
    return {
        "month_of_year": month,
        "quarter": quarter,
        "is_december": month == 12,
        "is_q4": quarter == 4,
    }


def calc_mom_growth(current: float, previous: float) -> float | None:
    """Month-over-month growth percentage."""
    if previous is None or previous == 0:
        return None
    return ((current - previous) / previous) * 100


def calc_yoy_growth(current: float, year_ago: float) -> float | None:
    """Year-over-year growth percentage."""
    if year_ago is None or year_ago == 0:
        return None
    return ((current - year_ago) / year_ago) * 100


def build_feature_row(
    state: str,
    industry: str,
    month: date,
    turnover: float,
    lag_values: dict[str, float | None],
    cpi_yoy_change: float | None = None,
) -> dict:
    """
    Assemble a single feature row combining all feature groups.
    This is what the PySpark pipeline produces per row.
    """
    seasonal = extract_seasonal_features(month)
    mom_growth = calc_mom_growth(turnover, lag_values.get("lag_1m"))
    yoy_growth = calc_yoy_growth(turnover, lag_values.get("lag_12m"))

    return {
        "state": state,
        "industry": industry,
        "month": month,
        "turnover_millions": turnover,
        "turnover_lag_1m": lag_values.get("lag_1m"),
        "turnover_lag_3m": lag_values.get("lag_3m"),
        "turnover_lag_6m": lag_values.get("lag_6m"),
        "turnover_lag_12m": lag_values.get("lag_12m"),
        **seasonal,
        "turnover_mom_growth": mom_growth,
        "turnover_yoy_growth": yoy_growth,
        "cpi_yoy_change": cpi_yoy_change,
    }


# ── Tests: Lag Features ──────────────────────────────────────────


class TestLagFeatures:
    """Tests for create_lag_features — pure list operations."""

    def test_lag_1_month(self):
        values = [100, 110, 120, 130, 140]
        lags = create_lag_features(values, lag=1)
        assert lags == [None, 100, 110, 120, 130]

    def test_lag_3_month(self):
        values = [100, 110, 120, 130, 140]
        lags = create_lag_features(values, lag=3)
        assert lags == [None, None, None, 100, 110]

    def test_lag_12_month(self):
        # 24 months of data: lag_12m should be None for first 12
        values = [1000 + i * 50 for i in range(24)]
        lags = create_lag_features(values, lag=12)
        # First 12 are None
        assert all(l is None for l in lags[:12])
        # From index 12 onward, lag matches values 12 months back
        assert lags[12] == values[0]   # 1000
        assert lags[13] == values[1]   # 1050
        assert lags[23] == values[11]  # 1550

    def test_lag_preserves_length(self):
        values = list(range(100))
        for lag in [1, 3, 6, 12]:
            result = create_lag_features(values, lag)
            assert len(result) == len(values)

    def test_lag_empty_list(self):
        assert create_lag_features([], lag=1) == []


# ── Tests: Seasonal Features ─────────────────────────────────────


class TestSeasonalFeatures:
    """Tests for extract_seasonal_features — date decomposition."""

    def test_january(self):
        result = extract_seasonal_features(date(2024, 1, 1))
        assert result["month_of_year"] == 1
        assert result["quarter"] == 1
        assert result["is_december"] is False
        assert result["is_q4"] is False

    def test_december(self):
        result = extract_seasonal_features(date(2024, 12, 1))
        assert result["month_of_year"] == 12
        assert result["quarter"] == 4
        assert result["is_december"] is True
        assert result["is_q4"] is True

    def test_q4_months(self):
        """October, November, December are Q4."""
        for month in [10, 11, 12]:
            result = extract_seasonal_features(date(2024, month, 1))
            assert result["is_q4"] is True, f"Month {month} should be Q4"
            assert result["quarter"] == 4

    def test_non_q4_months(self):
        """Months 1-9 are not Q4."""
        for month in range(1, 10):
            result = extract_seasonal_features(date(2024, month, 1))
            assert result["is_q4"] is False, f"Month {month} should not be Q4"

    def test_all_quarters(self):
        expected = {1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2,
                    7: 3, 8: 3, 9: 3, 10: 4, 11: 4, 12: 4}
        for month, quarter in expected.items():
            result = extract_seasonal_features(date(2024, month, 1))
            assert result["quarter"] == quarter, f"Month {month} → Q{quarter}"

    def test_only_december_is_december(self):
        for month in range(1, 13):
            result = extract_seasonal_features(date(2024, month, 1))
            assert result["is_december"] == (month == 12)


# ── Tests: Growth Features ───────────────────────────────────────


class TestGrowthFeatures:
    """Tests for MoM and YoY growth calculations."""

    def test_mom_positive_growth(self):
        # $4600M this month, $4500M last month → 2.22% growth
        assert calc_mom_growth(4600, 4500) == pytest.approx(2.2222, rel=1e-3)

    def test_mom_negative_growth(self):
        assert calc_mom_growth(4400, 4500) == pytest.approx(-2.2222, rel=1e-3)

    def test_mom_no_previous(self):
        """First month has no previous — returns None."""
        assert calc_mom_growth(4500, None) is None

    def test_mom_zero_previous(self):
        assert calc_mom_growth(4500, 0) is None

    def test_yoy_positive_growth(self):
        # $4500M now, $4200M a year ago → 7.14% growth
        assert calc_yoy_growth(4500, 4200) == pytest.approx(7.1429, rel=1e-3)

    def test_yoy_negative_growth(self):
        assert calc_yoy_growth(4000, 4200) == pytest.approx(-4.7619, rel=1e-3)

    def test_yoy_no_year_ago(self):
        assert calc_yoy_growth(4500, None) is None

    def test_realistic_food_retail_nsw(self):
        """Real-ish numbers: NSW Food retailing ~$4.5B/month."""
        jan_2024 = 4520.0
        jan_2023 = 4200.0
        dec_2023 = 4850.0  # December spike
        # YoY
        assert calc_yoy_growth(jan_2024, jan_2023) == pytest.approx(7.619, rel=1e-2)
        # MoM (Jan drops after December spike)
        assert calc_mom_growth(jan_2024, dec_2023) == pytest.approx(-6.804, rel=1e-2)


# ── Tests: Feature Row Assembly ──────────────────────────────────


class TestFeatureRowAssembly:
    """Tests for the complete feature row — all feature groups combined."""

    def test_complete_row_schema(self):
        row = build_feature_row(
            state="New South Wales",
            industry="Food retailing",
            month=date(2024, 6, 1),
            turnover=4600.0,
            lag_values={"lag_1m": 4500, "lag_3m": 4400, "lag_6m": 4300, "lag_12m": 4200},
            cpi_yoy_change=3.5,
        )
        expected_keys = {
            "state", "industry", "month", "turnover_millions",
            "turnover_lag_1m", "turnover_lag_3m", "turnover_lag_6m", "turnover_lag_12m",
            "month_of_year", "quarter", "is_december", "is_q4",
            "turnover_mom_growth", "turnover_yoy_growth", "cpi_yoy_change",
        }
        assert set(row.keys()) == expected_keys

    def test_key_columns_not_null(self):
        row = build_feature_row(
            state="Victoria",
            industry="Food retailing",
            month=date(2024, 3, 1),
            turnover=3900.0,
            lag_values={"lag_1m": 3800},
        )
        assert row["state"] is not None
        assert row["industry"] is not None
        assert row["month"] is not None
        assert row["turnover_millions"] is not None

    def test_lag_nulls_propagate(self):
        """Early rows missing lag values → growth features are None."""
        row = build_feature_row(
            state="Queensland",
            industry="Food retailing",
            month=date(2023, 1, 1),
            turnover=2900.0,
            lag_values={},  # No lag data (first month)
        )
        assert row["turnover_lag_1m"] is None
        assert row["turnover_lag_12m"] is None
        assert row["turnover_mom_growth"] is None
        assert row["turnover_yoy_growth"] is None

    def test_seasonal_features_in_row(self):
        row = build_feature_row(
            state="New South Wales",
            industry="Food retailing",
            month=date(2024, 12, 1),
            turnover=5200.0,
            lag_values={"lag_1m": 4800, "lag_12m": 4900},
        )
        assert row["month_of_year"] == 12
        assert row["quarter"] == 4
        assert row["is_december"] is True
        assert row["is_q4"] is True

    def test_growth_calculations_in_row(self):
        row = build_feature_row(
            state="New South Wales",
            industry="Food retailing",
            month=date(2024, 2, 1),
            turnover=4600.0,
            lag_values={"lag_1m": 4500, "lag_12m": 4200},
        )
        assert row["turnover_mom_growth"] == pytest.approx(2.2222, rel=1e-3)
        assert row["turnover_yoy_growth"] == pytest.approx(9.5238, rel=1e-3)
