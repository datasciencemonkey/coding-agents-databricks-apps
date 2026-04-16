"""Shared code mappings for ABS data decoding.

Used by silver layer transforms to decode integer codes from ABS SDMX API
into human-readable names.
"""

from __future__ import annotations

REGION_DECODE: dict[int, str] = {
    1: "New South Wales",
    2: "Victoria",
    3: "Queensland",
    4: "South Australia",
    5: "Western Australia",
    6: "Tasmania",
    7: "Northern Territory",
    8: "Australian Capital Territory",
}

INDUSTRY_DECODE: dict[int, str] = {
    20: "Food retailing",
    41: "Clothing, footwear and personal accessories",
    42: "Department stores",
    43: "Other retailing",
    44: "Cafes, restaurants and takeaway",
    45: "Household goods retailing",
}

INDEX_DECODE: dict[int, str] = {
    10001: "All groups CPI",
    20001: "Food and non-alcoholic beverages",
}

VOLUME_PATH = "/Volumes/workshop_vibe_coding/demo/raw_data"


def decode_column(column_name: str, mapping: dict[int, str]):
    """Build a PySpark when().otherwise() chain for integer-to-string decoding."""
    from pyspark.sql.functions import col, when, lit

    expr = lit("Unknown")
    for code, name in mapping.items():
        expr = when(col(column_name) == code, lit(name)).otherwise(expr)
    return expr
