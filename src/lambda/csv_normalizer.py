"""Lambda handler: validates and normalizes a CSV uploaded to the raw bucket,
then writes the cleaned CSV to the processed bucket.

Triggered by S3 ObjectCreated events (filtered to *.csv by the Terraform
notification config). Uses only the Python standard library, so no Lambda
layer is required.
"""
from __future__ import annotations

import csv
import io
import logging
import os
from pathlib import PurePosixPath

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

PROCESSED_BUCKET = os.environ["PROCESSED_BUCKET"]


def normalize_header(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def normalize_row(row: dict[str, str]) -> dict[str, str]:
    return {key: value.strip() for key, value in row.items()}


def handler(event: dict, context) -> dict:
    results = []

    for record in event["Records"]:
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = record["s3"]["object"]["key"]

        logger.info("Processing s3://%s/%s", source_bucket, source_key)

        response = s3.get_object(Bucket=source_bucket, Key=source_key)
        raw_text = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(raw_text))
        if not reader.fieldnames:
            raise ValueError(f"s3://{source_bucket}/{source_key} has no header row")

        normalized_fieldnames = [normalize_header(name) for name in reader.fieldnames]
        rows = [normalize_row(row) for row in reader]

        output_buffer = io.StringIO()
        writer = csv.DictWriter(output_buffer, fieldnames=normalized_fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(dict(zip(normalized_fieldnames, row.values())))

        processed_key = str(PurePosixPath(source_key))
        s3.put_object(
            Bucket=PROCESSED_BUCKET,
            Key=processed_key,
            Body=output_buffer.getvalue().encode("utf-8"),
            ContentType="text/csv",
        )

        logger.info(
            "Uploaded s3://%s/%s (%d rows)",
            PROCESSED_BUCKET,
            processed_key,
            len(rows),
        )
        results.append({"source": source_key, "processed": processed_key})

    return {"processed": results}
