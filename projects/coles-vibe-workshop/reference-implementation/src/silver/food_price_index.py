"""Silver layer: Food Price Index transformation.

Decodes series codes, parses dates, and standardizes column names
from the bronze ABS CPI Food table.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    when,
    lit,
    regexp_replace,
    to_date,
    concat,
    year,
    quarter as quarter_fn,
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

INDEX_DECODE = {
    "10001": "All groups CPI",
    "20001": "Food and non-alcoholic beverages",
}


@dp.expect_or_fail("valid_date", "date IS NOT NULL")
@dp.expect(
    "valid_state",
    "state IN ('New South Wales','Victoria','Queensland','South Australia',"
    "'Western Australia','Tasmania','Northern Territory','Australian Capital Territory')",
)
@dp.expect("positive_index", "cpi_index > 0")
@dp.table(
    comment="Cleaned CPI food price index with decoded regions and categories",
)
def silver_food_price_index():
    """Transform bronze CPI food data into analytics-ready silver table.

    - Decodes REGION codes to state names
    - Decodes INDEX_CODE to readable category names
    - Parses TIME_PERIOD (quarterly) to a proper date column
    - Renames OBS_VALUE to cpi_index
    - Filters to food-related categories only
    """
    spark = SparkSession.getActiveSession()

    # Build decode expressions
    region_expr = col("REGION").cast("string")
    for code, name in REGION_DECODE.items():
        region_expr = when(
            col("REGION").cast("string") == code, lit(name)
        ).otherwise(region_expr)

    index_expr = col("INDEX").cast("string")
    for code, name in INDEX_DECODE.items():
        index_expr = when(
            col("INDEX").cast("string") == code, lit(name)
        ).otherwise(index_expr)

    df = spark.read.table("LIVE.bronze_abs_cpi_food")

    return (
        df.withColumn("state", region_expr)
        .withColumn("category", index_expr)
        # Parse quarterly TIME_PERIOD (e.g. "2024-Q1") to date
        .withColumn(
            "date",
            to_date(
                concat(
                    col("TIME_PERIOD").substr(1, 4),
                    lit("-"),
                    when(col("TIME_PERIOD").contains("Q1"), lit("01"))
                    .when(col("TIME_PERIOD").contains("Q2"), lit("04"))
                    .when(col("TIME_PERIOD").contains("Q3"), lit("07"))
                    .when(col("TIME_PERIOD").contains("Q4"), lit("10")),
                    lit("-01"),
                ),
                "yyyy-MM-dd",
            ),
        )
        .withColumn("year", year("date"))
        .withColumn("quarter", quarter_fn("date"))
        .withColumnRenamed("OBS_VALUE", "cpi_index")
        .select(
            "state",
            "category",
            "date",
            "year",
            "quarter",
            "cpi_index",
        )
        .filter(col("date").isNotNull())
        .filter(col("cpi_index").isNotNull())
        .filter(col("category") == "Food and non-alcoholic beverages")
    )
