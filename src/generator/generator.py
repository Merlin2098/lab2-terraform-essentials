"""Generates random CSV files under data/ to test the datalake lab locally.

Usage:
    python src/generator/generator.py [--rows 100] [--files 1]

The alumno then uploads the generated CSV(s) to the "raw" S3 bucket to
trigger the CSV-to-Parquet Lambda.
"""
from __future__ import annotations

import argparse
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"

COLUMNS = ["id", "name", "signup_date", "amount"]
NAMES = ["Ana", "Luis", "Marta", "Carlos", "Sofia", "Diego", "Valentina", "Mateo"]


def random_row() -> list[str]:
    signup_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 600))
    return [
        str(uuid4()),
        random.choice(NAMES),
        signup_date.strftime("%Y-%m-%d"),
        f"{random.uniform(5, 500):.2f}",
    ]


def generate_csv(path: Path, rows: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(COLUMNS)
        for _ in range(rows):
            writer.writerow(random_row())


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate random CSV files for the lab.")
    parser.add_argument("--rows", type=int, default=100, help="Rows per CSV file.")
    parser.add_argument("--files", type=int, default=1, help="Number of CSV files to generate.")
    args = parser.parse_args()

    for _ in range(args.files):
        file_path = DATA_DIR / f"orders_{uuid4().hex[:8]}.csv"
        generate_csv(file_path, args.rows)
        print(file_path)


if __name__ == "__main__":
    main()
