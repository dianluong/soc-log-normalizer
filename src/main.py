"""
MVP 01 + MVP 02 + MVP 03 + MVP 04:
Safe Input File Inspection, CSV Schema Validation, CSV Field Normalization,
and CSV Field Validation Summary.

The script can:
- Inspect safe metadata for a local file.
- Validate a sanitized raw CSV schema.
- Normalize validated raw CSV fields into a new output file.
- Validate normalized CSV field values and print a summary report.

It does not modify, move, delete, upload, or execute input files.
"""

import argparse
import csv
import ipaddress
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Sequence

REQUIRED_COLUMNS = (
    "EventID",
    "TimeCreated",
    "TargetUserName",
    "IpAddress",
)

NORMALIZED_COLUMN_MAP = {
    "EventID": "event_id",
    "TimeCreated": "time_created",
    "TargetUserName": "target_user_name",
    "IpAddress": "ip_address",
}

NORMALIZED_COLUMNS = tuple(NORMALIZED_COLUMN_MAP.values())

EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 1
EXIT_NOT_CSV = 3
EXIT_MISSING_COLUMNS = 4
EXIT_CSV_ERROR = 5
EXIT_OUTPUT_ERROR = 6
EXIT_FIELD_VALIDATION_ERROR = 7


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect a local file, validate CSV schema, normalize CSV fields, "
            "or validate normalized CSV field values."
        )
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the file that should be inspected, validated, or normalized.",
    )

    mode_group = parser.add_mutually_exclusive_group()

    mode_group.add_argument(
        "--validate-csv",
        action="store_true",
        help="Validate required raw CSV columns and count data rows.",
    )

    mode_group.add_argument(
        "--normalize-csv",
        action="store_true",
        help="Normalize validated raw CSV fields into a new output file.",
    )

    mode_group.add_argument(
        "--validate-fields",
        action="store_true",
        help="Validate field values in a normalized CSV and print a summary.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Path for a new normalized CSV output file.",
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


def get_new_output_path(output_path: Path) -> Path | None:
    """
    Validate that an output path can be safely created.

    The function refuses to overwrite an existing file.
    """
    resolved_path = output_path.expanduser()

    if resolved_path.exists():
        print(
            f"ERROR: Output path already exists and will not be overwritten: "
            f"{resolved_path}",
            file=sys.stderr,
        )
        return None

    if not resolved_path.parent.exists():
        print(
            f"ERROR: Output directory does not exist: {resolved_path.parent}",
            file=sys.stderr,
        )
        return None

    if not resolved_path.parent.is_dir():
        print(
            f"ERROR: Output parent is not a directory: {resolved_path.parent}",
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
    Validate raw CSV extension, required column names, and data-row count.

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
                column
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


def normalize_csv(input_path: Path, output_path: Path) -> int:
    """
    Normalize validated raw CSV field names and trim whitespace from values.

    The input file is never changed. A new output file is created.
    """
    validation_status = validate_csv_schema(input_path)

    if validation_status != EXIT_SUCCESS:
        return validation_status

    resolved_input_path = get_existing_file_path(input_path)

    if resolved_input_path is None:
        return EXIT_INPUT_ERROR

    resolved_output_path = get_new_output_path(output_path)

    if resolved_output_path is None:
        return EXIT_OUTPUT_ERROR

    try:
        with resolved_input_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as input_file:
            reader = csv.DictReader(input_file)

            with resolved_output_path.open(
                mode="x",
                encoding="utf-8",
                newline="",
            ) as output_file:
                writer = csv.DictWriter(
                    output_file,
                    fieldnames=NORMALIZED_COLUMNS,
                )
                writer.writeheader()

                row_count = 0

                for row in reader:
                    normalized_row = {
                        normalized_column: (
                            row.get(source_column) or ""
                        ).strip()
                        for source_column, normalized_column
                        in NORMALIZED_COLUMN_MAP.items()
                    }

                    writer.writerow(normalized_row)
                    row_count += 1

    except (OSError, UnicodeDecodeError, csv.Error) as error:
        print(
            f"ERROR: Could not normalize CSV safely: {error}",
            file=sys.stderr,
        )
        return EXIT_CSV_ERROR

    print("CSV Field Normalization")
    print(f"Input path: {resolved_input_path}")
    print(f"Output path: {resolved_output_path}")
    print(f"Output columns: {', '.join(NORMALIZED_COLUMNS)}")
    print(f"Data rows written: {row_count}")
    print("Result: PASS")

    return EXIT_SUCCESS


def is_positive_integer(value: str) -> bool:
    """Return True when a value is a positive integer."""
    try:
        return int(value) > 0
    except ValueError:
        return False


def is_utc_timestamp(value: str) -> bool:
    """Return True when a value strictly matches YYYY-MM-DDTHH:MM:SSZ."""
    try:
        parsed_timestamp = datetime.strptime(
            value,
            "%Y-%m-%dT%H:%M:%SZ",
        )
    except ValueError:
        return False

    return parsed_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ") == value


def is_valid_ipv4(value: str) -> bool:
    """Return True when a value is a valid IPv4 address."""
    try:
        parsed_address = ipaddress.ip_address(value)
    except ValueError:
        return False

    return parsed_address.version == 4


def validate_normalized_csv_schema(
    input_path: Path,
) -> tuple[int, Path | None, list[str] | None]:
    """
    Validate a normalized CSV file before field-level validation.

    Returns:
        Exit code, resolved input path, and detected columns.
    """
    resolved_path = get_existing_file_path(input_path)

    if resolved_path is None:
        return EXIT_INPUT_ERROR, None, None

    if resolved_path.suffix.lower() != ".csv":
        print(
            f"ERROR: Field validation requires a .csv file: {resolved_path.name}",
            file=sys.stderr,
        )
        return EXIT_NOT_CSV, None, None

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
                return EXIT_CSV_ERROR, None, None

            detected_columns = [
                column
                for column in reader.fieldnames
                if column is not None
            ]

    except (OSError, UnicodeDecodeError, csv.Error) as error:
        print(
            f"ERROR: Could not read CSV safely: {error}",
            file=sys.stderr,
        )
        return EXIT_CSV_ERROR, None, None

    missing_columns = [
        column
        for column in NORMALIZED_COLUMNS
        if column not in detected_columns
    ]

    if missing_columns:
        print("Normalized CSV Schema Validation")
        print(f"Path: {resolved_path}")
        print(f"Detected columns: {', '.join(detected_columns)}")
        print(f"Missing columns: {', '.join(missing_columns)}")
        print("Result: FAIL")
        return EXIT_MISSING_COLUMNS, None, None

    return EXIT_SUCCESS, resolved_path, detected_columns


def validate_fields(input_path: Path) -> int:
    """
    Validate field values in a normalized CSV and print a summary report.

    The function does not modify the input CSV or create output files.
    """
    status, resolved_path, detected_columns = validate_normalized_csv_schema(
        input_path
    )

    if status != EXIT_SUCCESS or resolved_path is None:
        return status

    issue_counts: Counter[str] = Counter()
    total_rows = 0
    valid_rows = 0
    invalid_rows = 0

    try:
        with resolved_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                total_rows += 1
                row_has_issue = False

                event_id = (row.get("event_id") or "").strip()
                time_created = (row.get("time_created") or "").strip()
                target_user_name = (
                    row.get("target_user_name") or ""
                ).strip()
                ip_address = (row.get("ip_address") or "").strip()

                if not is_positive_integer(event_id):
                    issue_counts["invalid_event_id"] += 1
                    row_has_issue = True

                if not is_utc_timestamp(time_created):
                    issue_counts["invalid_time_created"] += 1
                    row_has_issue = True

                if not target_user_name:
                    issue_counts["empty_target_user_name"] += 1
                    row_has_issue = True

                if not is_valid_ipv4(ip_address):
                    issue_counts["invalid_ip_address"] += 1
                    row_has_issue = True

                if row_has_issue:
                    invalid_rows += 1
                else:
                    valid_rows += 1

    except (OSError, UnicodeDecodeError, csv.Error) as error:
        print(
            f"ERROR: Could not validate CSV fields safely: {error}",
            file=sys.stderr,
        )
        return EXIT_CSV_ERROR

    print("CSV Field Validation Summary")
    print(f"Path: {resolved_path}")
    print(f"Detected columns: {', '.join(detected_columns)}")
    print(f"Total rows: {total_rows}")
    print(f"Valid rows: {valid_rows}")
    print(f"Invalid rows: {invalid_rows}")
    print()
    print("Validation issues:")

    if issue_counts:
        for issue_name in (
            "invalid_event_id",
            "invalid_time_created",
            "empty_target_user_name",
            "invalid_ip_address",
        ):
            print(f"- {issue_name}: {issue_counts[issue_name]}")
    else:
        print("- none")

    if invalid_rows == 0:
        print("Result: PASS")
        return EXIT_SUCCESS

    print("Result: FAIL")
    return EXIT_FIELD_VALIDATION_ERROR


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI application."""
    args = parse_args(argv)

    if args.output is not None and not args.normalize_csv:
        print(
            "ERROR: --output is only supported when using --normalize-csv.",
            file=sys.stderr,
        )
        return EXIT_OUTPUT_ERROR

    if args.normalize_csv:
        if args.output is None:
            print(
                "ERROR: --output is required when using --normalize-csv.",
                file=sys.stderr,
            )
            return EXIT_OUTPUT_ERROR

        return normalize_csv(args.input, args.output)

    if args.validate_fields:
        return validate_fields(args.input)

    if args.validate_csv:
        return validate_csv_schema(args.input)

    return inspect_input_file(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
