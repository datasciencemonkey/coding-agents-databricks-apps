"""Gold layer: Food Inflation Year-over-Year.

Calculates year-over-year inflation rates from the silver food price
index, aggregated by state and quarter.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    lag,
    round as round_,
)
from pyspark.sql.window import Window


@dp.expect("valid_yoy_change", "yoy_change_pct BETWEEN -50 AND 100")
@dp.table(
    comment="Year-over-year food inflation rate by state and quarter",
)
def gold_food_inflation_yoy():
    """Calculate year-over-year CPI change percentage for food.

    Compares each quarter's CPI index to the same quarter one year prior
    to derive the annual inflation rate by state.
    """
    spark = SparkSession.getActiveSession()

    df = spark.read.table("LIVE.silver_food_price_index")

    # Window: partition by state, order by date, look back 4 quarters
    window_yoy = (
        Window.partitionBy("state")
        .orderBy("date")
    )

    return (
        df.withColumn(
            "prev_year_index",
            lag("cpi_index", 4).over(window_yoy),
        )
        .withColumn(
            "yoy_change_pct",
            round_(
                (col("cpi_index") - col("prev_year_index"))
                / col("prev_year_index")
                * 100,
                2,
            ),
        )
        .filter(col("prev_year_index").isNotNull())
        .select(
            "state",
            "category",
            "date",
            "year",
            "quarter",
            "cpi_index",
            "yoy_change_pct",
        )
        .orderBy("state", "date")
    )
