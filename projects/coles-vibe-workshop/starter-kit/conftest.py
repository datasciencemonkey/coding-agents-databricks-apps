"""
Shared pytest fixtures for workshop tests.
Provides a SparkSession and sample DataFrames matching the ABS API schemas.
"""

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType


@pytest.fixture(scope="session")
def spark():
    """Create a local SparkSession for testing. Shared across all tests."""
    return (
        SparkSession.builder
        .master("local[*]")
        .appName("workshop-tests")
        .getOrCreate()
    )


@pytest.fixture
def sample_retail_csv(spark):
    """
    Sample ABS Retail Trade data matching the bronze table schema.
    Columns mirror what the API returns in CSV format.

    REGION codes: 1=NSW, 2=VIC, 3=QLD
    INDUSTRY codes: 20=Food retailing, 41=Clothing
    """
    schema = StructType([
        StructField("DATAFLOW", StringType()),
        StructField("FREQ", StringType()),
        StructField("MEASURE", StringType()),
        StructField("INDUSTRY", StringType()),
        StructField("REGION", StringType()),
        StructField("TIME_PERIOD", StringType()),
        StructField("OBS_VALUE", DoubleType()),
    ])
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
def sample_cpi_csv(spark):
    """
    Sample ABS CPI Food data matching the bronze table schema.

    INDEX codes: 10001=All groups CPI, 20001=Food and non-alcoholic beverages
    REGION codes: 1=NSW, 2=VIC
    """
    schema = StructType([
        StructField("DATAFLOW", StringType()),
        StructField("FREQ", StringType()),
        StructField("MEASURE", StringType()),
        StructField("INDEX", StringType()),
        StructField("REGION", StringType()),
        StructField("TIME_PERIOD", StringType()),
        StructField("OBS_VALUE", DoubleType()),
    ])
    data = [
        ("ABS:CPI", "Q", "1", "10001", "1", "2024-Q1", 136.4),
        ("ABS:CPI", "Q", "1", "20001", "1", "2024-Q1", 142.8),
        ("ABS:CPI", "Q", "1", "10001", "2", "2024-Q1", 134.9),
        ("ABS:CPI", "Q", "1", "20001", "2", "2024-Q1", 140.2),
        ("ABS:CPI", "Q", "1", "10001", "1", "2024-Q2", 137.1),
    ]
    return spark.createDataFrame(data, schema)
