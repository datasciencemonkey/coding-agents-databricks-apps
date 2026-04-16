"""Silver layer: Retail Turnover transformation.

Decodes region and industry codes, parses dates, and renames columns
from the bronze ABS Retail Trade table.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    to_date,
    month,
    year,
    quarter,
    when,
    concat,
    lit,
)


REGION_DECODE = {
    "1": "New South Wales",
    "2": "Victoria",
    "3": "Queensland",
    "4": "South Australia",
    "5": "Western Australia",
    "6": "Tasmania",
    "7": "Northern Territory",
    "8": "Australian Capital Territory",
}

INDUSTRY_DECODE = {
    "20": "Food retailing",
    "41": "Clothing, footwear and personal accessories",
    "42": "Department stores",
    "43": "Other retailing",
    "44": "Cafes, restaurants and takeaway",
    "45": "Household goods retailing",
}


def _build_when_chain(col_name, mapping):
    """Build a chained when() expression from a dictionary mapping."""
    expr = None
    for code, name in mapping.items():
        condition = when(col(col_name).cast("string") == code, lit(name))
        expr = condition if expr is None else expr.when(
            col(col_name).cast("string") == code, lit(name)
        )
    return expr.otherwise(col(col_name).cast("string"))


@dp.expect_or_fail("valid_date", "date IS NOT NULL")
@dp.expect(
    "valid_state",
    "state IN ('New South Wales','Victoria','Queensland','South Australia',"
    "'Western Australia','Tasmania','Northern Territory','Australian Capital Territory')",
)
@dp.expect("positive_turnover", "turnover_millions > 0")
@dp.table(
    comment="Cleaned retail turnover with decoded regions and industries",
)
def silver_retail_turnover():
    """Transform bronze retail trade data into analytics-ready silver table.

    - Decodes REGION codes to state names
    - Decodes INDUSTRY codes to readable industry names
    - Parses TIME_PERIOD to a proper date column
    - Renames OBS_VALUE to turnover_millions
    """
    spark = SparkSession.getActiveSession()

    # Build decode expressions
    region_expr = col("REGION").cast("string")
    for code, name in REGION_DECODE.items():
        region_expr = when(
            col("REGION").cast("string") == code, lit(name)
        ).otherwise(region_expr)

    industry_expr = col("INDUSTRY").cast("string")
    for code, name in INDUSTRY_DECODE.items():
        industry_expr = when(
            col("INDUSTRY").cast("string") == code, lit(name)
        ).otherwise(industry_expr)

    df = spark.read.table("LIVE.bronze_abs_retail_trade")

    return (
        df.withColumn("state", region_expr)
        .withColumn("industry", industry_expr)
        .withColumn("date", to_date(concat(col("TIME_PERIOD"), lit("-01")), "yyyy-MM-dd"))
        .withColumn("year", year("date"))
        .withColumn("month", month("date"))
        .withColumn("quarter", quarter("date"))
        .withColumnRenamed("OBS_VALUE", "turnover_millions")
        .select(
            "state",
            "industry",
            "date",
            "year",
            "month",
            "quarter",
            "turnover_millions",
        )
        .filter(col("date").isNotNull())
        .filter(col("turnover_millions").isNotNull())
    )
