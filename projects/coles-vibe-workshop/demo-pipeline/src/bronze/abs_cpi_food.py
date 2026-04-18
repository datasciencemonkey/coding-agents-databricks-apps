# Databricks notebook source
"""Bronze: ABS Consumer Price Index (Food) ingestion."""

try:
    import databricks.declarative_pipelines as dp
except ModuleNotFoundError:
    import dlt as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


@dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
@dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")
@dp.table(comment="Raw ABS CPI data — quarterly food price indices by state since 2010")
def bronze_abs_cpi_food():
    spark = SparkSession.getActiveSession()
    return (
        spark.read.csv(
            "/Volumes/workshop_vibe_coding/demo/raw_data/abs_cpi_food.csv",
            header=True, inferSchema=True,
        )
        .withColumn("_ingested_at", current_timestamp())
    )
