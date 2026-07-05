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