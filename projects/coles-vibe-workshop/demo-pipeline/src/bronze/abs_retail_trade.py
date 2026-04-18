# Databricks notebook source
"""Bronze: ABS Retail Trade ingestion."""

try:
    import databricks.declarative_pipelines as dp
except ModuleNotFoundError:
    import dlt as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


@dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
@dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")
@dp.table(comment="Raw ABS Retail Trade data — monthly turnover by state and industry since 2010")
def bronze_abs_retail_trade():
    spark = SparkSession.getActiveSession()
    return (
        spark.read.csv(
            "/Volumes/workshop_vibe_coding/demo/raw_data/abs_retail_trade.csv",
            header=True, inferSchema=True,
        )
        .withColumn("_ingested_at", current_timestamp())
    )
