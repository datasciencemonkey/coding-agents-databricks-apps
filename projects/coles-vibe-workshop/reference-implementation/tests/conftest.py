"""
Shared pytest fixtures for the Grocery Intelligence Platform reference implementation.

Provides a SparkSession and sample DataFrames matching the ABS API schemas
for bronze, silver, and gold layer testing.
"""

import os
import tempfile
from datetime import date
from decimal import Decimal

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    DateType,
    DecimalType,
    DoubleType,
    IntegerType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)


@pytest.fixture(scope="session")
def spark(tmp_path_factory):
    """Create a local SparkSession for testing. Shared across all tests."""
    warehouse_dir = str(tmp_path_factory.mktemp("spark-warehouse"))
    session = (
        SparkSession.builder.master("local[*]")
        .appName("grocery-intelligence-tests")
        .config("spark.sql.warehouse.dir", warehouse_dir)
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.driver.bindAddress", "127.0.0.1")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield session
    session.stop()


# ── Bronze Fixtures ──────────────────────────────────────────────────


@pytest.fixture
def sample_retail_csv(spark):
    """
    Sample ABS Retail Trade data matching the raw API CSV schema.
    6 rows covering 3 states, 2 industries, 2 months.

    REGION codes: 1=NSW, 2=VIC, 3=QLD
    INDUSTRY codes: 20=Food retailing, 41=Clothing/footwear/personal
    """
    schema = StructType(
        [
            StructField("DATAFLOW", StringType()),
            StructField("FREQ", StringType()),
            StructField("MEASURE", StringType()),
            StructField("INDUSTRY", StringType()),
            StructField("REGION", StringType()),
            StructField("TIME_PERIOD", StringType()),
            StructField("OBS_VALUE", DoubleType()),
        ]
    )
    data = [
        ("ABS:RT", "M", "M1", "20", "1", "2024-01", 4500.0),
        ("ABS:RT", "M", "M1", "20", "2", "2024-01", 3800.0),
        ("ABS:RT", "M", "M1", "20", "3", "2024-01", 2900.0),
        ("ABS:RT", "M", "M1", "41", "1", "2024-01", 1200.0),
        ("ABS:RT", "M", "M1", "20", "1", "2024-02", 4600.0),
        ("ABS:RT", "M", "M1", "20", "2", "2024-02", 3900.0),
    ]
    return spark.createDataFrame(data, schema)


@pytest.fixture
def sample_retail_csv_with_nulls(spark):
    """
    Sample ABS Retail Trade data containing null values.
    Used to test null filtering in silver layer.
    """
    schema = StructType(
        [
            StructField("DATAFLOW", StringType()),
            StructField("FREQ", StringType()),
            StructField("MEASURE", StringType()),
            StructField("INDUSTRY", StringType()),
            StructField("REGION", StringType()),
            StructField("TIME_PERIOD", StringType()),
            StructField("OBS_VALUE", DoubleType()),
        ]
    )
    data = [
        ("ABS:RT", "M", "M1", "20", "1", "2024-01", 4500.0),
        ("ABS:RT", "M", "M1", "20", "2", "2024-01", None),
        ("ABS:RT", "M", "M1", "20", "3", None, 2900.0),
        ("ABS:RT", "M", "M1", "20", "1", "2024-02", 4600.0),
        ("ABS:RT", "M", "M1", "41", "1", "2024-01", 1200.0),
    ]
    return spark.createDataFrame(data, schema)


@pytest.fixture
def sample_cpi_csv(spark):
    """
    Sample ABS CPI Food data matching the raw API CSV schema.
    5 rows covering 2 states, 2 index types, 2 quarters.

    INDEX codes: 10001=All groups CPI, 20001=Food and non-alcoholic beverages
    REGION codes: 1=NSW, 2=VIC
    """
    schema = StructType(
        [
            StructField("DATAFLOW", StringType()),
            StructField("FREQ", StringType()),
            StructField("MEASURE", StringType()),
            StructField("INDEX", StringType()),
            StructField("REGION", StringType()),
            StructField("TIME_PERIOD", StringType()),
            StructField("OBS_VALUE", DoubleType()),
        ]
    )
    data = [
        ("ABS:CPI", "Q", "1", "10001", "1", "2024-Q1", 136.4),
        ("ABS:CPI", "Q", "1", "20001", "1", "2024-Q1", 142.8),
        ("ABS:CPI", "Q", "1", "10001", "2", "2024-Q1", 134.9),
        ("ABS:CPI", "Q", "1", "20001", "2", "2024-Q1", 140.2),
        ("ABS:CPI", "Q", "1", "10001", "1", "2024-Q2", 137.1),
    ]
    return spark.createDataFrame(data, schema)


# ── Silver Fixtures ──────────────────────────────────────────────────


@pytest.fixture
def sample_silver_retail(spark):
    """
    Silver-layer retail turnover data: decoded states, industries, proper dates.
    24 rows covering 2 years of monthly data for NSW Food retailing.
    Used for gold-layer aggregation tests.
    """
    schema = StructType(
        [
            StructField("date", DateType()),
            StructField("state", StringType()),
            StructField("industry", StringType()),
            StructField("turnover_millions", DoubleType()),
            StructField("month", IntegerType()),
            StructField("year", IntegerType()),
            StructField("quarter", IntegerType()),
        ]
    )
    # 24 months of NSW Food retailing data: Jan 2023 - Dec 2024
    # Turnover grows ~2% month-on-month with seasonal variation
    data = [
        (date(2023, 1, 1), "New South Wales", "Food retailing", 4200.0, 1, 2023, 1),
        (date(2023, 2, 1), "New South Wales", "Food retailing", 4100.0, 2, 2023, 1),
        (date(2023, 3, 1), "New South Wales", "Food retailing", 4300.0, 3, 2023, 1),
        (date(2023, 4, 1), "New South Wales", "Food retailing", 4250.0, 4, 2023, 2),
        (date(2023, 5, 1), "New South Wales", "Food retailing", 4150.0, 5, 2023, 2),
        (date(2023, 6, 1), "New South Wales", "Food retailing", 4350.0, 6, 2023, 2),
        (date(2023, 7, 1), "New South Wales", "Food retailing", 4400.0, 7, 2023, 3),
        (date(2023, 8, 1), "New South Wales", "Food retailing", 4300.0, 8, 2023, 3),
        (date(2023, 9, 1), "New South Wales", "Food retailing", 4500.0, 9, 2023, 3),
        (date(2023, 10, 1), "New South Wales", "Food retailing", 4450.0, 10, 2023, 4),
        (date(2023, 11, 1), "New South Wales", "Food retailing", 4550.0, 11, 2023, 4),
        (date(2023, 12, 1), "New South Wales", "Food retailing", 4800.0, 12, 2023, 4),
        (date(2024, 1, 1), "New South Wales", "Food retailing", 4500.0, 1, 2024, 1),
        (date(2024, 2, 1), "New South Wales", "Food retailing", 4400.0, 2, 2024, 1),
        (date(2024, 3, 1), "New South Wales", "Food retailing", 4600.0, 3, 2024, 1),
        (date(2024, 4, 1), "New South Wales", "Food retailing", 4550.0, 4, 2024, 2),
        (date(2024, 5, 1), "New South Wales", "Food retailing", 4450.0, 5, 2024, 2),
        (date(2024, 6, 1), "New South Wales", "Food retailing", 4650.0, 6, 2024, 2),
        (date(2024, 7, 1), "New South Wales", "Food retailing", 4700.0, 7, 2024, 3),
        (date(2024, 8, 1), "New South Wales", "Food retailing", 4600.0, 8, 2024, 3),
        (date(2024, 9, 1), "New South Wales", "Food retailing", 4800.0, 9, 2024, 3),
        (date(2024, 10, 1), "New South Wales", "Food retailing", 4750.0, 10, 2024, 4),
        (date(2024, 11, 1), "New South Wales", "Food retailing", 4850.0, 11, 2024, 4),
        (date(2024, 12, 1), "New South Wales", "Food retailing", 5100.0, 12, 2024, 4),
    ]
    return spark.createDataFrame(data, schema)


@pytest.fixture
def sample_silver_cpi(spark):
    """
    Silver-layer CPI food price index data: decoded states, indices, proper dates.
    8 quarters covering 2 years for NSW, Food and non-alcoholic beverages.
    Used for gold-layer inflation calculation tests.
    """
    schema = StructType(
        [
            StructField("date", DateType()),
            StructField("state", StringType()),
            StructField("index_name", StringType()),
            StructField("cpi_index", DoubleType()),
            StructField("quarter", IntegerType()),
            StructField("year", IntegerType()),
        ]
    )
    # 8 quarters of NSW Food CPI data: Q1 2023 - Q4 2024
    # CPI rises ~1-2% per quarter (food inflation)
    data = [
        (date(2023, 1, 1), "New South Wales", "Food and non-alcoholic beverages", 130.0, 1, 2023),
        (date(2023, 4, 1), "New South Wales", "Food and non-alcoholic beverages", 132.5, 2, 2023),
        (date(2023, 7, 1), "New South Wales", "Food and non-alcoholic beverages", 134.8, 3, 2023),
        (date(2023, 10, 1), "New South Wales", "Food and non-alcoholic beverages", 136.2, 4, 2023),
        (date(2024, 1, 1), "New South Wales", "Food and non-alcoholic beverages", 137.8, 1, 2024),
        (date(2024, 4, 1), "New South Wales", "Food and non-alcoholic beverages", 139.5, 2, 2024),
        (date(2024, 7, 1), "New South Wales", "Food and non-alcoholic beverages", 141.0, 3, 2024),
        (date(2024, 10, 1), "New South Wales", "Food and non-alcoholic beverages", 142.3, 4, 2024),
    ]
    return spark.createDataFrame(data, schema)


# ── Gold Fixtures ────────────────────────────────────────────────────


@pytest.fixture
def sample_gold_retail(spark):
    """
    Gold-layer retail summary with rolling averages and YoY growth.
    Used for data quality tests.
    """
    schema = StructType(
        [
            StructField("date", DateType()),
            StructField("state", StringType()),
            StructField("industry", StringType()),
            StructField("turnover_millions", DoubleType()),
            StructField("turnover_3m_avg", DoubleType()),
            StructField("turnover_12m_avg", DoubleType()),
            StructField("yoy_growth_pct", DoubleType()),
        ]
    )
    data = [
        (date(2024, 1, 1), "New South Wales", "Food retailing", 4500.0, 4483.3, 4362.5, 7.14),
        (date(2024, 2, 1), "New South Wales", "Food retailing", 4400.0, 4566.7, 4370.8, 7.32),
        (date(2024, 3, 1), "New South Wales", "Food retailing", 4600.0, 4500.0, 4391.7, 6.98),
        (date(2024, 1, 1), "Victoria", "Food retailing", 3800.0, 3766.7, 3675.0, 5.56),
        (date(2024, 2, 1), "Victoria", "Food retailing", 3700.0, 3800.0, 3683.3, 5.71),
    ]
    return spark.createDataFrame(data, schema)


@pytest.fixture
def sample_gold_cpi(spark):
    """
    Gold-layer food inflation with YoY change percentage.
    Used for data quality tests.
    """
    schema = StructType(
        [
            StructField("date", DateType()),
            StructField("state", StringType()),
            StructField("index_name", StringType()),
            StructField("cpi_index", DoubleType()),
            StructField("yoy_change_pct", DoubleType()),
        ]
    )
    data = [
        (date(2024, 1, 1), "New South Wales", "Food and non-alcoholic beverages", 137.8, 6.0),
        (date(2024, 4, 1), "New South Wales", "Food and non-alcoholic beverages", 139.5, 5.28),
        (date(2024, 7, 1), "New South Wales", "Food and non-alcoholic beverages", 141.0, 4.60),
        (date(2024, 10, 1), "New South Wales", "Food and non-alcoholic beverages", 142.3, 4.48),
    ]
    return spark.createDataFrame(data, schema)
