"""
MVP 01 + MVP 02 + MVP 03:
Safe Input File Inspection, CSV Schema Validation, and CSV Field Normalization.

The script can:
- Inspect safe metadata for a local file.
- Validate a sanitized CSV schema.
- Normalize validated CSV fields into a new output file.

It does not modify, move, delete, or upload input files.
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


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Inspect a local file, validate CSV schema, or normalize CSV fields."
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
        help="Validate required columns and count CSV data rows.",
    )

    mode_group.add_argument(
        "--normalize-csv",
        action="store_true",
        help="Normalize validated CSV fields into a new output file.",
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
    Normalize validated CSV field names and trim whitespace from field values.

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


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI application."""
    args = parse_args(argv)

    if args.normalize_csv:
        if args.output is None:
            print(
                "ERROR: --output is required when using --normalize-csv.",
                file=sys.stderr,
            )
            return EXIT_OUTPUT_ERROR

        return normalize_csv(args.input, args.output)

    if args.validate_csv:
        return validate_csv_schema(args.input)

    return inspect_input_file(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
