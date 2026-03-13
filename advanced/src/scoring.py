"""
Insurance Claims Risk Scoring
Reads ingested claims from Unity Catalog and applies a rule-based risk scoring model.
In production this would call an MLflow model; here we use deterministic rules for demo purposes.
"""

import argparse
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, StringType


def get_spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def compute_risk_score(claim_amount, claim_type, claimant_age, prior_claims_count):
    """
    Rule-based risk scoring (mock ML model).

    Factors:
    - High claim amount (>50k) adds risk
    - Liability claims are higher risk
    - Younger claimants (<30) and older (>60) add risk
    - Prior claims history increases risk
    """
    score = 0.0

    # Amount factor
    if claim_amount > 100000:
        score += 40
    elif claim_amount > 50000:
        score += 25
    elif claim_amount > 10000:
        score += 10

    # Claim type factor
    type_risk = {
        "liability": 30,
        "property_fire": 20,
        "auto_collision": 10,
        "auto_theft": 15,
        "property_water": 12,
    }
    score += type_risk.get(claim_type, 5)

    # Age factor
    if claimant_age < 30:
        score += 15
    elif claimant_age > 60:
        score += 10

    # Prior claims factor
    score += min(prior_claims_count * 8, 30)

    return min(score, 100.0)


def risk_label(score):
    if score >= 60:
        return "HIGH"
    elif score >= 35:
        return "MEDIUM"
    else:
        return "LOW"


# Register UDFs
compute_risk_score_udf = F.udf(compute_risk_score, DoubleType())
risk_label_udf = F.udf(risk_label, StringType())


def main():
    parser = argparse.ArgumentParser(description="Score claims for risk")
    parser.add_argument("--catalog", required=True, help="Unity Catalog catalog name")
    parser.add_argument("--schema", required=True, help="Unity Catalog schema name")
    args = parser.parse_args()

    spark = get_spark()

    source_table = f"{args.catalog}.{args.schema}.raw_claims"
    target_table = f"{args.catalog}.{args.schema}.scored_claims"

    print(f"[SCORING] Reading claims from {source_table}")
    df = spark.read.table(source_table)
    print(f"[SCORING] Processing {df.count()} claims")

    # Apply risk scoring model
    scored_df = df.withColumn(
        "risk_score",
        compute_risk_score_udf(
            F.col("claim_amount"),
            F.col("claim_type"),
            F.col("claimant_age"),
            F.col("prior_claims_count"),
        )
    ).withColumn(
        "risk_label",
        risk_label_udf(F.col("risk_score"))
    ).withColumn(
        "scored_at",
        F.current_timestamp()
    )

    # Show results for demo
    print("[SCORING] Risk scoring results:")
    scored_df.select(
        "claim_id", "claim_amount", "claim_type", "risk_score", "risk_label"
    ).show(truncate=False)

    # Write to Unity Catalog
    scored_df.write.mode("overwrite").saveAsTable(target_table)

    # Summary stats
    summary = scored_df.groupBy("risk_label").agg(
        F.count("*").alias("count"),
        F.round(F.avg("claim_amount"), 2).alias("avg_claim_amount"),
        F.round(F.avg("risk_score"), 2).alias("avg_risk_score"),
    )
    print("[SCORING] Risk distribution summary:")
    summary.show(truncate=False)

    print(f"[SCORING] Successfully wrote scored claims to {target_table}")
    print("[SCORING] DABs Demo — Risk Scoring Complete")


if __name__ == "__main__":
    main()
