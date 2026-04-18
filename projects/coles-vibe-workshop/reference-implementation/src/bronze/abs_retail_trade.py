"""Bronze layer: ABS Retail Trade ingestion.

Ingests raw CSV data from the ABS SDMX API for monthly retail turnover
by state and industry. No transformations — raw columns preserved.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


@dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
@dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")
@dp.table(
    comment="Raw ABS Retail Trade data from SDMX API",
)
def bronze_abs_retail_trade():
    """Ingest ABS Retail Trade CSV from the SDMX API.

    Fetches monthly retail turnover by state and industry since 2010.
    Falls back to checkpoint table if the API is unavailable.
    """
    spark = SparkSession.getActiveSession()

    api_url = (
        "https://api.data.abs.gov.au/data/ABS,RT,1.0.0/"
        "M1.20+41+42+43+44+45.20.1+2+3+4+5+6+7+8.M"
        "?format=csv&startPeriod=2010-01"
    )

    try:
        df = (
            spark.read.csv(api_url, header=True, inferSchema=True)
            .withColumn("_ingested_at", current_timestamp())
        )
        # Verify we got data
        if df.first() is None:
            raise ValueError("Empty response from ABS Retail Trade API")
        return df
    except Exception:
        # Fallback: read from pre-loaded checkpoint table
        return (
            spark.read.table("workshop_vibe_coding.checkpoints.abs_retail_trade")
            .withColumn("_ingested_at", current_timestamp())
        )
