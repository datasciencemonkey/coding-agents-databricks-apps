# Databricks notebook source
"""Gold: Retail Summary — monthly turnover with rolling averages and YoY growth."""

try:
    import databricks.declarative_pipelines as dp
except ModuleNotFoundError:
    import dlt as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as sum_, avg, lag, round as round_
from pyspark.sql.window import Window


@dp.expect("valid_yoy", "yoy_growth_pct BETWEEN -100 AND 500")
@dp.expect("valid_rolling_avg", "turnover_3m_avg > 0")
@dp.table(comment="Monthly retail summary by state with rolling averages and YoY growth")
def gold_retail_summary():
    spark = SparkSession.getActiveSession()
    df = spark.read.table("LIVE.silver_retail_turnover")

    monthly = (
        df.groupBy("state", "date", "year", "month")
        .agg(sum_("turnover_millions").alias("total_turnover"))
    )

    w3 = Window.partitionBy("state").orderBy("date").rowsBetween(-2, 0)
    w12 = Window.partitionBy("state").orderBy("date").rowsBetween(-11, 0)
    wyoy = Window.partitionBy("state").orderBy("date")

    return (
        monthly
        .withColumn("turnover_3m_avg", round_(avg("total_turnover").over(w3), 2))
        .withColumn("turnover_12m_avg", round_(avg("total_turnover").over(w12), 2))
        .withColumn("prev_year_turnover", lag("total_turnover", 12).over(wyoy))
        .withColumn(
            "yoy_growth_pct",
            round_(
                (col("total_turnover") - col("prev_year_turnover"))
                / col("prev_year_turnover") * 100,
                2,
            ),
        )
        .drop("prev_year_turnover")
        .orderBy("state", "date")
    )
