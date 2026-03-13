"""
Insurance Claims Data Ingestion
Reads raw claims from the landing zone and writes to Unity Catalog as a managed Delta table.
"""

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, TimestampType, IntegerType
)
from datetime import datetime


def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def create_mock_claims(spark: SparkSession):
    """Generate mock claims data simulating a daily landing zone drop."""
    schema = StructType([
        StructField("claim_id", StringType(), False),
        StructField("policy_number", StringType(), False),
        StructField("claim_date", TimestampType(), False),
        StructField("claim_amount", DoubleType(), False),
        StructField("claim_type", StringType(), False),
        StructField("claimant_age", IntegerType(), False),
        StructField("region", StringType(), False),
        StructField("prior_claims_count", IntegerType(), False),
    ])

    data = [
        ("CLM-001", "POL-10042", datetime(2025, 3, 10), 12500.00, "auto_collision", 34, "northeast", 1),
        ("CLM-002", "POL-20087", datetime(2025, 3, 10), 75000.00, "property_fire", 55, "southeast", 0),
        ("CLM-003", "POL-10042", datetime(2025, 3, 11), 3200.00, "auto_theft", 34, "northeast", 2),
        ("CLM-004", "POL-30190", datetime(2025, 3, 11), 150000.00, "liability", 28, "west", 0),
        ("CLM-005", "POL-40321", datetime(2025, 3, 12), 8900.00, "auto_collision", 45, "midwest", 3),
        ("CLM-006", "POL-50010", datetime(2025, 3, 12), 22000.00, "property_water", 62, "southeast", 1),
    ]

    return spark.createDataFrame(data, schema)


def main():
    parser = argparse.ArgumentParser(description="Ingest claims data into Unity Catalog")
    parser.add_argument("--catalog", required=True, help="Unity Catalog catalog name")
    parser.add_argument("--schema", required=True, help="Unity Catalog schema name")
    parser.add_argument("--landing-zone", required=True, help="Landing zone volume path")
    args = parser.parse_args()

    spark = get_spark()

    print(f"[INGEST] Catalog: {args.catalog}, Schema: {args.schema}")
    print(f"[INGEST] Landing zone: {args.landing_zone}")

    # In production this would read from the landing zone:
    #   df = spark.read.format("json").load(args.landing_zone)
    # For demo purposes we generate mock data:
    df = create_mock_claims(spark)

    table_name = f"{args.catalog}.{args.schema}.raw_claims"
    print(f"[INGEST] Writing {df.count()} claims to {table_name}")

    df.write.mode("overwrite").saveAsTable(table_name)

    print(f"[INGEST] Successfully wrote claims to {table_name}")
    print("[INGEST] DABs Demo — Ingestion Complete")


if __name__ == "__main__":
    main()
