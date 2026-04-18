# Databricks notebook source
"""Silver: Retail Turnover — decode regions/industries, cast dates."""

try:
    import databricks.declarative_pipelines as dp
except ModuleNotFoundError:
    import dlt as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, month, year, quarter, when, lit

REGION_DECODE = {
    1: "New South Wales", 2: "Victoria", 3: "Queensland", 4: "South Australia",
    5: "Western Australia", 6: "Tasmania", 7: "Northern Territory", 8: "Australian Capital Territory",
}
INDUSTRY_DECODE = {
    20: "Food retailing", 41: "Clothing, footwear and personal accessories",
    42: "Department stores", 43: "Other retailing",
    44: "Cafes, restaurants and takeaway", 45: "Household goods retailing",
}


def _decode(column, mapping):
    expr = lit("Unknown")
    for code, name in mapping.items():
        expr = when(col(column) == code, lit(name)).otherwise(expr)
    return expr


@dp.expect_or_fail("valid_date", "date IS NOT NULL")
@dp.expect(
    "valid_state",
    "state IN ('New South Wales','Victoria','Queensland','South Australia',"
    "'Western Australia','Tasmania','Northern Territory','Australian Capital Territory')",
)
@dp.expect("positive_turnover", "turnover_millions > 0")
@dp.table(comment="Cleaned retail turnover with decoded regions and industries")
def silver_retail_turnover():
    spark = SparkSession.getActiveSession()
    df = spark.read.table("LIVE.bronze_abs_retail_trade")

    return (
        df.withColumn("state", _decode("REGION", REGION_DECODE))
        .withColumn("industry", _decode("INDUSTRY", INDUSTRY_DECODE))
        .withColumn("date", col("TIME_PERIOD").cast("date"))
        .withColumn("year", year("date"))
        .withColumn("month", month("date"))
        .withColumn("quarter", quarter("date"))
        .withColumnRenamed("OBS_VALUE", "turnover_millions")
        .select("state", "industry", "date", "year", "month", "quarter", "turnover_millions")
        .filter(col("date").isNotNull())
        .filter(col("turnover_millions").isNotNull())
        .filter(col("turnover_millions") > 0)
    )
