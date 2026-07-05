"""
MVP 01 + MVP 02: Safe Input File Inspection and CSV Schema Validation CLI.

The script can:
- Inspect safe metadata for a local file.
- Validate a sanitized CSV schema before future normalization steps.

It does not modify, move, delete, or upload files.
"""

import argparse
import csv
import sys
from pathlib import Path
from typing import Sequence

REQUIRED_COLUMNS = (
    "EventID",
    "TimeCreated",
    "TargetUserName",
    "IpAddress",
)

EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 1
EXIT_NOT_CSV = 3
EXIT_MISSING_COLUMNS = 4
EXIT_CSV_ERROR = 5


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Inspect a local file or validate a CSV schema."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the file that should be inspected or validated.",
    )

    parser.add_argument(
        "--validate-csv",
        action="store_true",
        help="Validate required columns and count CSV data rows.",
    )

    return parser.parse_args(argv)


def get_existing_file_path(input_path: Path) -> Path | None:
    """
    Validate that an input path exists and points to a file.

    Returns:
        Resolved Path when valid, otherwise None.
    """
    resolved_path = input_path.expanduser()

    if not resolved_path.exists():
        print(
            f"ERROR: Input path does not exist: {resolved_path}",
            file=sys.stderr,
        )
        return None

    if not resolved_path.is_file():
        print(
            f"ERROR: Input path is not a file: {resolved_path}",
            file=sys.stderr,
        )
        return None

    return resolved_path.resolve()


def inspect_input_file(input_path: Path) -> int:
    """Print safe metadata for an existing input file."""
    resolved_path = get_existing_file_path(input_path)

    if resolved_path is None:
        return EXIT_INPUT_ERROR

    try:
        file_size = resolved_path.stat().st_size
    except OSError as error:
        print(
            f"ERROR: Could not inspect file metadata: {error}",
            file=sys.stderr,
        )
        return EXIT_INPUT_ERROR

    extension = resolved_path.suffix if resolved_path.suffix else "(no extension)"

    print("Input File Inspection")
    print(f"Path: {resolved_path}")
    print("Exists: True")
    print(f"Extension: {extension}")
    print(f"Size (bytes): {file_size}")

    return EXIT_SUCCESS


def validate_csv_schema(input_path: Path) -> int:
    """
    Validate CSV extension, required column names, and data-row count.

    The function does not normalize fields or change CSV contents.
    """
    resolved_path = get_existing_file_path(input_path)

    if resolved_path is None:
        return EXIT_INPUT_ERROR

    if resolved_path.suffix.lower() != ".csv":
        print(
            f"ERROR: CSV validation requires a .csv file: {resolved_path.name}",
            file=sys.stderr,
        )
        return EXIT_NOT_CSV

    try:
        with resolved_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                print(
                    "ERROR: CSV header row was not found.",
                    file=sys.stderr,
                )
                return EXIT_CSV_ERROR

            detected_columns = [
                column.strip()
                for column in reader.fieldnames
                if column is not None
            ]

            missing_columns = [
                column
                for column in REQUIRED_COLUMNS
                if column not in detected_columns
            ]

            if missing_columns:
                print("CSV Schema Validation")
                print(f"Path: {resolved_path}")
                print(f"Detected columns: {', '.join(detected_columns)}")
                print(f"Missing columns: {', '.join(missing_columns)}")
                print("Result: FAIL")
                return EXIT_MISSING_COLUMNS

            row_count = sum(1 for _ in reader)

    except (OSError, UnicodeDecodeError, csv.Error) as error:
        print(
            f"ERROR: Could not read CSV safely: {error}",
            file=sys.stderr,
        )
        return EXIT_CSV_ERROR

    print("CSV Schema Validation")
    print(f"Path: {resolved_path}")
    print(f"Detected columns: {', '.join(detected_columns)}")
    print(f"Required columns: {', '.join(REQUIRED_COLUMNS)}")
    print(f"Data rows: {row_count}")

    if row_count == 0:
        print("Result: PASS (schema valid; no data rows)")
    else:
        print("Result: PASS")

    return EXIT_SUCCESS


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI application."""
    args = parse_args(argv)

    if args.validate_csv:
        return validate_csv_schema(args.input)

    return inspect_input_file(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
