"""Gold layer: Grocery Insights cross-source view.

Joins retail turnover summary with food inflation data and food recall
counts to produce a single analytics-ready table.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col,
    count,
    coalesce,
    lit,
    trunc,
    to_date,
    month as month_fn,
    year as year_fn,
)


@dp.expect("has_state", "state IS NOT NULL")
@dp.expect("has_date", "month IS NOT NULL")
@dp.table(
    comment="Cross-source grocery insights joining retail, inflation, and recalls",
)
def gold_grocery_insights():
    """Join retail summary, food inflation, and food recalls into one view.

    - Retail data is monthly; CPI data is quarterly. Joins on state + quarter.
    - Food recalls are left-joined by state + month (recall_count may be 0).
    """
    spark = SparkSession.getActiveSession()

    retail = spark.read.table("LIVE.gold_retail_summary")
    inflation = spark.read.table("LIVE.gold_food_inflation_yoy")

    # Prepare retail: add quarter for join
    retail_q = (
        retail
        .withColumn("month", trunc("date", "month"))
        .withColumn("join_quarter", trunc("date", "quarter"))
    )

    # Prepare inflation: add quarter key for join
    inflation_q = (
        inflation
        .withColumn("join_quarter", trunc("date", "quarter"))
        .select(
            col("state").alias("inf_state"),
            col("join_quarter").alias("inf_quarter"),
            "yoy_change_pct",
        )
        .dropDuplicates(["inf_state", "inf_quarter"])
    )

    # Join retail with inflation on state + quarter
    joined = (
        retail_q.join(
            inflation_q,
            (retail_q["state"] == inflation_q["inf_state"])
            & (retail_q["join_quarter"] == inflation_q["inf_quarter"]),
            "left",
        )
    )

    # Prepare food recalls — count by state and month
    try:
        recalls = spark.read.table("LIVE.bronze_fsanz_food_recalls")
        recalls_monthly = (
            recalls
            .withColumn("recall_month", trunc(to_date("recall_date"), "month"))
            .groupBy(
                col("states_affected").alias("recall_state"),
                "recall_month",
            )
            .agg(count("*").alias("recall_count"))
        )

        result = (
            joined.join(
                recalls_monthly,
                (joined["state"] == recalls_monthly["recall_state"])
                & (joined["month"] == recalls_monthly["recall_month"]),
                "left",
            )
            .withColumn("recall_count", coalesce("recall_count", lit(0)))
        )
    except Exception:
        # FSANZ data may not be available — continue without it
        result = joined.withColumn("recall_count", lit(0))

    return result.select(
        "state",
        "month",
        "total_turnover",
        "turnover_3m_avg",
        "yoy_growth_pct",
        col("yoy_change_pct").alias("cpi_yoy_change"),
        "recall_count",
    )
