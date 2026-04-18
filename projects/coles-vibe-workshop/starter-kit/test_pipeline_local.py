"""
Fast local tests that run WITHOUT Spark or Java.
Test transformation LOGIC separately from Spark execution.
"""
import pytest


# ── Pattern: Extract transformation logic into pure Python functions ──

def decode_region(code: str) -> str:
    """Decode ABS region code to state name."""
    mapping = {
        "1": "New South Wales", "2": "Victoria", "3": "Queensland",
        "4": "South Australia", "5": "Western Australia", "6": "Tasmania",
        "7": "Northern Territory", "8": "Australian Capital Territory",
    }
    return mapping.get(str(code), f"Unknown ({code})")


def decode_industry(code: str) -> str:
    """Decode ABS industry code to name."""
    mapping = {
        "20": "Food retailing", "41": "Clothing, footwear and personal accessories",
        "42": "Department stores", "43": "Other retailing",
        "44": "Cafes, restaurants and takeaway", "45": "Household goods retailing",
    }
    return mapping.get(str(code), f"Unknown ({code})")


def parse_time_period(tp: str) -> tuple:
    """Parse ABS TIME_PERIOD to (year, month, day)."""
    if "-Q" in tp:
        year, q = tp.split("-Q")
        month = (int(q) - 1) * 3 + 1
        return (int(year), month, 1)
    else:
        parts = tp.split("-")
        return (int(parts[0]), int(parts[1]), 1)


def calc_yoy_growth(current: float, previous: float) -> float:
    """Calculate year-over-year growth percentage."""
    if previous == 0:
        return 0.0
    return ((current - previous) / previous) * 100


# ── Tests: Pure Python, no Spark, sub-second execution ──────────

class TestDecodeRegion:
    def test_nsw(self):
        assert decode_region("1") == "New South Wales"

    def test_vic(self):
        assert decode_region("2") == "Victoria"

    def test_all_states(self):
        for code in range(1, 9):
            result = decode_region(str(code))
            assert "Unknown" not in result, f"Code {code} not mapped"

    def test_unknown_code(self):
        assert "Unknown" in decode_region("99")


class TestDecodeIndustry:
    def test_food_retailing(self):
        assert decode_industry("20") == "Food retailing"

    def test_clothing(self):
        assert "Clothing" in decode_industry("41")

    def test_unknown(self):
        assert "Unknown" in decode_industry("999")


class TestTimePeriodParsing:
    def test_monthly(self):
        assert parse_time_period("2024-01") == (2024, 1, 1)

    def test_quarterly(self):
        assert parse_time_period("2024-Q1") == (2024, 1, 1)
        assert parse_time_period("2024-Q2") == (2024, 4, 1)
        assert parse_time_period("2024-Q3") == (2024, 7, 1)
        assert parse_time_period("2024-Q4") == (2024, 10, 1)


class TestYoYGrowth:
    def test_positive_growth(self):
        assert calc_yoy_growth(110, 100) == pytest.approx(10.0)

    def test_negative_growth(self):
        assert calc_yoy_growth(90, 100) == pytest.approx(-10.0)

    def test_zero_previous(self):
        assert calc_yoy_growth(100, 0) == 0.0

    def test_realistic_retail(self):
        # Jan 2024: $4500M, Jan 2023: $4200M → 7.14% growth
        assert calc_yoy_growth(4500, 4200) == pytest.approx(7.142857, rel=1e-3)
