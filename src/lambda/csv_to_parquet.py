"""Lambda handler: converts a CSV uploaded to the raw bucket into Parquet
and writes it to the processed bucket.

Triggered by S3 ObjectCreated events (filtered to *.csv by the Terraform
notification config). Uses pandas/pyarrow from the AWS SDK for pandas
Lambda layer.
"""
from __future__ import annotations

import logging
import os
from pathlib import PurePosixPath

import boto3
import pandas as pd

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

PROCESSED_BUCKET = os.environ["PROCESSED_BUCKET"]


def handler(event: dict, context) -> dict:
    results = []

    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = record["s3"]["object"]["key"]

        logger.info("Processing s3://%s/%s", source_bucket, source_key)

        local_csv_path = f"/tmp/{PurePosixPath(source_key).name}"
        s3.download_file(source_bucket, source_key, local_csv_path)

        dataframe = pd.read_csv(local_csv_path)

        parquet_key = str(PurePosixPath(source_key).with_suffix(".parquet"))
        local_parquet_path = f"/tmp/{PurePosixPath(parquet_key).name}"
        dataframe.to_parquet(local_parquet_path, index=False)

        s3.upload_file(local_parquet_path, PROCESSED_BUCKET, parquet_key)

        logger.info(
            "Uploaded s3://%s/%s (%d rows)",
            PROCESSED_BUCKET,
            parquet_key,
            len(dataframe),
        )
        results.append({"source": source_key, "processed": parquet_key})

    return {"processed": results}
