"""End-to-end validation of the CSV normalizer pipeline.

Uploads the first CSV found in the project's `data/` folder to the raw S3
bucket, waits for the Lambda (triggered by the S3 ObjectCreated notification)
to write the normalized output to the processed bucket, and asserts the
output content is well-formed.

Requires infrastructure to already be deployed (`terraform apply` from
`infra/`) and AWS credentials configured in the environment. Bucket names are
resolved from `terraform output -json`, never hardcoded.

Run with:
    pytest tests/aws/test_e2e_upload.py -v
"""
from __future__ import annotations

import csv
import io
import json
import subprocess
import time
from pathlib import Path

import boto3
import pytest
from botocore.exceptions import ClientError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFRA_DIR = PROJECT_ROOT / "infra"
DATA_DIR = PROJECT_ROOT / "data"

POLL_INTERVAL_SECONDS = 2
POLL_TIMEOUT_SECONDS = 60


def _terraform_outputs() -> dict:
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=INFRA_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


@pytest.fixture(scope="module")
def outputs() -> dict:
    try:
        return _terraform_outputs()
    except subprocess.CalledProcessError as exc:
        pytest.fail(
            "Could not read terraform outputs from infra/. "
            f"Is the infrastructure deployed? stderr: {exc.stderr}"
        )


@pytest.fixture(scope="module")
def raw_bucket(outputs: dict) -> str:
    return outputs["raw_bucket_name"]["value"]


@pytest.fixture(scope="module")
def processed_bucket(outputs: dict) -> str:
    return outputs["processed_bucket_name"]["value"]


@pytest.fixture(scope="module")
def sample_csv() -> Path:
    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        pytest.fail(f"No CSV files found in {DATA_DIR}. Add one to run the E2E test.")
    return csv_files[0]


@pytest.fixture(scope="module")
def s3_client():
    return boto3.client("s3")


def _wait_for_object(s3_client, bucket: str, key: str, timeout: int = POLL_TIMEOUT_SECONDS):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            return s3_client.get_object(Bucket=bucket, Key=key)
        except ClientError as exc:
            if exc.response["Error"]["Code"] != "NoSuchKey":
                raise
            time.sleep(POLL_INTERVAL_SECONDS)
    pytest.fail(
        f"Timed out after {timeout}s waiting for s3://{bucket}/{key} "
        "to be created by the normalizer Lambda."
    )


def test_uploaded_csv_is_normalized_end_to_end(s3_client, raw_bucket, processed_bucket, sample_csv):
    key = sample_csv.name

    s3_client.upload_file(str(sample_csv), raw_bucket, key)

    try:
        response = _wait_for_object(s3_client, processed_bucket, key)
        processed_body = response["Body"].read().decode("utf-8")

        reader = csv.DictReader(io.StringIO(processed_body))
        assert reader.fieldnames, "Processed CSV has no header row"
        for header in reader.fieldnames:
            assert header == header.strip().lower().replace(" ", "_"), (
                f"Header {header!r} was not normalized"
            )

        rows = list(reader)
        assert rows, "Processed CSV has no data rows"
        for row in rows:
            for value in row.values():
                assert value == (value or "").strip(), f"Value {value!r} was not trimmed"
    finally:
        s3_client.delete_object(Bucket=raw_bucket, Key=key)
        s3_client.delete_object(Bucket=processed_bucket, Key=key)
