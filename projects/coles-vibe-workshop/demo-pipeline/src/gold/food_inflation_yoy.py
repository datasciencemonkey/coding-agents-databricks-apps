# Databricks notebook source
"""Gold: Food Inflation YoY — quarterly CPI change by state."""

try:
    import databricks.declarative_pipelines as dp
except ModuleNotFoundError:
    import dlt as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, round as round_
from pyspark.sql.window import Window


@dp.expect("valid_yoy_change", "yoy_change_pct BETWEEN -50 AND 100")
@dp.table(comment="Year-over-year CPI inflation rate by state and quarter")
def gold_food_inflation_yoy():
    spark = SparkSession.getActiveSession()
    df = spark.read.table("LIVE.silver_food_price_index")

    wyoy = Window.partitionBy("state").orderBy("date")

    return (
        df.withColumn("prev_year_index", lag("cpi_index", 4).over(wyoy))
        .withColumn(
            "yoy_change_pct",
            round_(
                (col("cpi_index") - col("prev_year_index"))
                / col("prev_year_index") * 100,
                2,
            ),
        )
        .filter(col("prev_year_index").isNotNull())
        .select("state", "category", "date", "year", "quarter", "cpi_index", "yoy_change_pct")
        .orderBy("state", "date")
    )
