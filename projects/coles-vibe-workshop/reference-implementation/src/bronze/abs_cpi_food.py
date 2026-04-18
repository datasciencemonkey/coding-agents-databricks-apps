"""Bronze layer: ABS Consumer Price Index (Food) ingestion.

Ingests raw CSV data from the ABS SDMX API for quarterly CPI food
indices by state. No transformations — raw columns preserved.
"""

import databricks.declarative_pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp


@dp.expect("valid_time_period", "TIME_PERIOD IS NOT NULL")
@dp.expect("valid_obs_value", "OBS_VALUE IS NOT NULL")
@dp.table(
    comment="Raw ABS CPI Food data from SDMX API",
)
def bronze_abs_cpi_food():
    """Ingest ABS CPI Food CSV from the SDMX API.

    Fetches quarterly food price indices by state since 2010.
    Falls back to checkpoint table if the API is unavailable.
    """
    spark = SparkSession.getActiveSession()

    api_url = (
        "https://api.data.abs.gov.au/data/ABS,CPI,2.0.0/"
        "1.10001+20001.10.1+2+3+4+5+6+7+8.Q"
        "?format=csv&startPeriod=2010-Q1"
    )

    try:
        df = (
            spark.read.csv(api_url, header=True, inferSchema=True)
            .withColumn("_ingested_at", current_timestamp())
        )
        if df.first() is None:
            raise ValueError("Empty response from ABS CPI API")
        return df
    except Exception:
        return (
            spark.read.table("workshop_vibe_coding.checkpoints.abs_cpi_food")
            .withColumn("_ingested_at", current_timestamp())
        )
