"""
MVP 01: Safe Input File Inspection CLI.

This script checks whether an input file exists and prints safe metadata.
It does not read, parse, modify, or upload the file.
"""

import argparse
import sys
from pathlib import Path
from typing import Sequence


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Inspect basic metadata for a local input file."
    )

    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to the file that should be inspected.",
    )

    return parser.parse_args(argv)


def inspect_input_file(input_path: Path) -> int:
    """
    Validate an input path and print safe file metadata.

    Returns:
        0 when inspection succeeds.
        1 when the path is invalid or cannot be inspected.
    """
    resolved_path = input_path.expanduser()

    if not resolved_path.exists():
        print(
            f"ERROR: Input path does not exist: {resolved_path}",
            file=sys.stderr,
        )
        return 1

    if not resolved_path.is_file():
        print(
            f"ERROR: Input path is not a file: {resolved_path}",
            file=sys.stderr,
        )
        return 1

    try:
        file_size = resolved_path.stat().st_size
    except OSError as error:
        print(
            f"ERROR: Could not inspect file metadata: {error}",
            file=sys.stderr,
        )
        return 1

    extension = resolved_path.suffix if resolved_path.suffix else "(no extension)"

    print("Input File Inspection")
    print(f"Path: {resolved_path.resolve()}")
    print("Exists: True")
    print(f"Extension: {extension}")
    print(f"Size (bytes): {file_size}")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI application."""
    args = parse_args(argv)
    return inspect_input_file(args.input)


if __name__ == "__main__":
    raise SystemExit(main())
