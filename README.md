# SOC Log Normalizer

> A small Python learning project for SOC log handling and security automation.

## Status

Scaffold stage — the repository structure and project rules are in place.
The log normalizer CLI has not been implemented yet.

## Objective

Build a small Python command-line tool that can:

- Read sanitized CSV or JSON log exports.
- Validate required fields.
- Normalize common fields into a consistent format.
- Write a safe output file for later analysis.

## Why This Project

SOC analysts often receive logs from different systems with inconsistent field names and formats.

This project is intended to practice:

- Python file handling
- CSV and JSON parsing
- Input validation
- Error handling
- Command-line arguments with `argparse`
- Safe handling of untrusted log data
- Documentation and testing for a public portfolio

## Scope

The first MVP will support:

- One input file at a time
- CSV and JSON input
- Sanitized sample data only
- A simple normalized output file
- Clear error messages for unsupported files or malformed records

## Non-Goals

This project will not:

- Connect to a real SIEM
- Process production logs
- Execute commands found inside log fields
- Replace a full log pipeline or SIEM
- Include real customer, organization, or endpoint data

## Planned Input Fields

The MVP will gradually standardize fields such as:

- `timestamp`
- `hostname`
- `username`
- `event_id`
- `source_ip`
- `destination_ip`
- `process_name`
- `message`

The exact supported fields will be documented after the first working version is verified.

## Repository Structure

```text
soc-log-normalizer/
├── .github/
│   └── copilot-instructions.md
├── docs/
├── sample-data/
├── src/
│   └── main.py
├── tests/
├── .gitignore
├── README.md
└── requirements.txt

## MVP 01 — Safe Input File Inspection

Implemented capability:

- Accepts an input file through `--input`.
- Validates that the path exists.
- Validates that the path is a file, not a directory.
- Prints safe metadata: resolved path, extension, and size in bytes.
- Returns explicit exit codes for invalid input.

Run:

```powershell
python .\src\main.py --input .\sample-data\sample.txt
```

Verification evidence:

- `docs/mvp-01-verification.md`

Current limitations:

- No CSV/JSON parsing yet.
- No event normalization yet.
- No automated tests yet.

## MVP 02 — CSV Schema Validation

Implemented capability:

- Accepts `--input <path>` and optional `--validate-csv`.
- Preserves MVP 01 safe input-file inspection when `--validate-csv` is not used.
- Rejects non-CSV input during CSV validation.
- Validates these required CSV columns:
  - `EventID`
  - `TimeCreated`
  - `TargetUserName`
  - `IpAddress`
- Reports detected columns, missing required columns, and data-row count.
- Handles a valid schema with zero data rows.
- Returns explicit exit codes for success and expected validation failures.

Run:

```powershell
python .\src\main.py --input .\sample-data\valid-events.csv --validate-csv
```

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | Validation passed |
| `1` | Input path is invalid or does not exist |
| `3` | CSV validation was requested for a non-CSV file |
| `4` | Required CSV columns are missing |
| `5` | CSV could not be read safely |

Verification evidence:

- `docs/mvp-02-verification.md`

Current limitations:

- Only CSV input is supported.
- Required column names must match exactly.
- Field values, timestamps, IP addresses, and Event IDs are not validated yet.
- No event normalization or output-file generation exists yet.
- No automated tests exist yet.

## MVP 03 — CSV Field Normalization

Implemented capability:

- Accepts `--input <path> --normalize-csv --output <new-output.csv>`.
- Runs CSV schema validation before normalization.
- Renames source columns to a consistent output schema:
  - `EventID` → `event_id`
  - `TimeCreated` → `time_created`
  - `TargetUserName` → `target_user_name`
  - `IpAddress` → `ip_address`
- Trims leading and trailing whitespace from field values.
- Preserves input row order.
- Creates a new output CSV without modifying the input file.
- Refuses to overwrite an existing output file.

Run:

```powershell
python .\src\main.py --input .\sample-data\messy-events.csv --normalize-csv --output .\sample-output\messy-events.normalized.csv
```

Exit codes:

| Code | Meaning |
|---:|---|
| `0` | Normalization completed successfully |
| `1` | Input path is invalid or does not exist |
| `3` | CSV operation was requested for a non-CSV file |
| `4` | Required CSV columns are missing |
| `5` | CSV could not be read safely |
| `6` | Output argument/path is unsafe or output already exists |

Verification evidence:

- `docs/mvp-03-verification.md`

Current limitations:

- Only CSV input is supported.
- Source header names must match exactly.
- Field values are trimmed but not semantically validated.
- No Event ID, timestamp, username, or IP validation exists yet.
- No detection, aggregation, or reporting logic exists yet.
- No automated tests exist yet.
