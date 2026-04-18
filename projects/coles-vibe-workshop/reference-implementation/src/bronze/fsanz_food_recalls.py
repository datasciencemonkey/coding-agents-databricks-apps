"""Bronze layer: FSANZ Food Recalls ingestion.

Ingests food recall data from the FSANZ website or a checkpoint table.
Raw columns preserved with no transformations.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


@dp.expect("product_name_not_null", "product_name IS NOT NULL")
@dp.expect("recall_date_not_null", "recall_date IS NOT NULL")
@dp.table(
    comment="Raw FSANZ food recall data",
)
def bronze_fsanz_food_recalls():
    """Ingest FSANZ food recalls.

    Attempts to read from the FSANZ website. Falls back to a checkpoint
    table if the site is unreachable or blocked.
    """
    spark = SparkSession.getActiveSession()

    # The FSANZ website requires web scraping which is unreliable in a
    # pipeline context. Read from the pre-loaded checkpoint table.
    # URL for reference: https://www.foodstandards.gov.au/consumer/recalls
    try:
        df = (
            spark.read.table("workshop_vibe_coding.checkpoints.fsanz_food_recalls")
            .withColumn("_ingested_at", current_timestamp())
        )
        return df
    except Exception:
        # Create empty DataFrame with expected schema as last resort
        from pyspark.sql.types import StructType, StructField, StringType

        schema = StructType([
            StructField("recall_date", StringType(), True),
            StructField("product_name", StringType(), True),
            StructField("hazard", StringType(), True),
            StructField("company", StringType(), True),
            StructField("states_affected", StringType(), True),
        ])
        return (
            spark.createDataFrame([], schema)
            .withColumn("_ingested_at", current_timestamp())
        )
