"""Upload every CSV in the project's `data/` folder to the raw S3 bucket.

This is a real data load, not a test: uploaded files are left in the bucket
so the normalizer Lambda can process them (triggered by the S3 ObjectCreated
notification). After uploading, the script waits briefly for the Lambda to
run and downloads its CloudWatch log events into `logs/` in the project root.

Requires infrastructure to already be deployed (`terraform apply` from
`infra/`). AWS credentials are loaded automatically from `.env.credentials`
in the project root (see `.env.example`). The raw bucket name and log group
name are resolved from `terraform output -json`, never hardcoded.

Run with:
    python scripts/aws/upload_data_to_raw.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INFRA_DIR = PROJECT_ROOT / "infra"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
ENV_CREDENTIALS_FILE = PROJECT_ROOT / ".env.credentials"

LOG_PROPAGATION_DELAY_SECONDS = 10


def _terraform_outputs() -> dict:
    result = subprocess.run(
        ["terraform", "output", "-json"],
        cwd=INFRA_DIR,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def _download_log_events(logs_client, log_group_name: str, since_epoch_ms: int) -> list[dict]:
    events = []
    kwargs = {
        "logGroupName": log_group_name,
        "startTime": since_epoch_ms,
        "interleaved": True,
    }
    while True:
        try:
            response = logs_client.filter_log_events(**kwargs)
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "ResourceNotFoundException":
                return events
            raise
        events.extend(response.get("events", []))
        next_token = response.get("nextToken")
        if not next_token:
            return events
        kwargs["nextToken"] = next_token


def main() -> int:
    if not ENV_CREDENTIALS_FILE.exists():
        print(
            f"{ENV_CREDENTIALS_FILE} not found. Copy .env.example to "
            ".env.credentials and fill in real AWS credentials.",
            file=sys.stderr,
        )
        return 1
    load_dotenv(ENV_CREDENTIALS_FILE, override=True)

    try:
        outputs = _terraform_outputs()
    except subprocess.CalledProcessError as exc:
        print(
            "Could not read terraform outputs from infra/. "
            f"Is the infrastructure deployed? stderr: {exc.stderr}",
            file=sys.stderr,
        )
        return 1

    raw_bucket = outputs["raw_bucket_name"]["value"]
    log_group_name = outputs["log_group_name"]["value"]

    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}.", file=sys.stderr)
        return 1

    upload_started_at = datetime.now(timezone.utc)
    since_epoch_ms = int(upload_started_at.timestamp() * 1000)

    s3_client = boto3.client("s3")
    for csv_file in csv_files:
        key = csv_file.name
        s3_client.upload_file(str(csv_file), raw_bucket, key)
        print(f"[OK] Uploaded s3://{raw_bucket}/{key}")

    print(f"Waiting {LOG_PROPAGATION_DELAY_SECONDS}s for the Lambda to run and emit logs...")
    time.sleep(LOG_PROPAGATION_DELAY_SECONDS)

    logs_client = boto3.client("logs")
    events = _download_log_events(logs_client, log_group_name, since_epoch_ms)

    LOGS_DIR.mkdir(exist_ok=True)
    log_file = LOGS_DIR / f"{upload_started_at.strftime('%Y%m%dT%H%M%SZ')}.log"
    with log_file.open("w", encoding="utf-8") as f:
        for event in events:
            event_time = datetime.fromtimestamp(event["timestamp"] / 1000, tz=timezone.utc)
            f.write(f"{event_time.isoformat()} {event['message'].rstrip()}\n")

    print(f"[OK] Saved {len(events)} log events from {log_group_name} to {log_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
