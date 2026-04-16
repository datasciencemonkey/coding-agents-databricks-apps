"""Gold layer: Retail Summary aggregation.

Aggregates silver retail turnover by state and month, then calculates
rolling averages and year-over-year growth rates.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    sum as sum_,
    avg,
    lag,
    round as round_,
)
from pyspark.sql.window import Window


@dp.expect("valid_yoy", "yoy_growth_pct BETWEEN -100 AND 500")
@dp.expect("valid_rolling_avg", "turnover_3m_avg > 0")
@dp.table(
    comment="Monthly retail summary by state with rolling averages and YoY growth",
)
def gold_retail_summary():
    """Aggregate retail turnover by state and month.

    Calculates:
    - total_turnover: sum of turnover across industries per state/month
    - turnover_3m_avg: 3-month rolling average
    - turnover_12m_avg: 12-month rolling average
    - yoy_growth_pct: year-over-year growth percentage
    """
    spark = SparkSession.getActiveSession()

    df = spark.read.table("LIVE.silver_retail_turnover")

    # Aggregate by state and date (monthly)
    monthly = (
        df.groupBy("state", "date", "year", "month")
        .agg(sum_("turnover_millions").alias("total_turnover"))
    )

    # Window for rolling averages — partition by state, order by date
    window_3m = (
        Window.partitionBy("state")
        .orderBy("date")
        .rowsBetween(-2, 0)
    )
    window_12m = (
        Window.partitionBy("state")
        .orderBy("date")
        .rowsBetween(-11, 0)
    )

    # Window for YoY — look back 12 months
    window_yoy = (
        Window.partitionBy("state")
        .orderBy("date")
    )

    return (
        monthly
        .withColumn("turnover_3m_avg", round_(avg("total_turnover").over(window_3m), 2))
        .withColumn("turnover_12m_avg", round_(avg("total_turnover").over(window_12m), 2))
        .withColumn(
            "prev_year_turnover",
            lag("total_turnover", 12).over(window_yoy),
        )
        .withColumn(
            "yoy_growth_pct",
            round_(
                (col("total_turnover") - col("prev_year_turnover"))
                / col("prev_year_turnover")
                * 100,
                2,
            ),
        )
        .drop("prev_year_turnover")
        .orderBy("state", "date")
    )
