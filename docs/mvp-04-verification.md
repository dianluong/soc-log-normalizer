# MVP 04 Verification - CSV Field Validation Summary

## Objective

Verify that `src/main.py` can validate field values in a normalized CSV and print a read-only summary report.

## Required Normalized Schema

```text
event_id
time_created
target_user_name
ip_address
```

## Field Validation Rules

| Field | Rule |
|---|---|
| `event_id` | Must be a positive integer. |
| `time_created` | Must strictly match `YYYY-MM-DDTHH:MM:SSZ`. |
| `target_user_name` | Must not be empty after trimming whitespace. |
| `ip_address` | Must be a valid IPv4 address. |

## Exit Codes

| Code | Meaning |
|---:|---|
| `0` | All rows are valid. |
| `1` | Input path is invalid or does not exist. |
| `2` | Command-line arguments are invalid. |
| `3` | A CSV operation was requested for a non-CSV file. |
| `4` | Required normalized CSV columns are missing. |
| `5` | CSV could not be read safely. |
| `6` | `--output` was used outside `--normalize-csv`. |
| `7` | One or more rows contain invalid field values. |

## Test 1 - Invalid Field Summary

Command:

```powershell
python .\src\main.py --input .\sample-data\normalized-field-validation.csv --validate-fields
```

Expected behavior:

- Detects six total rows.
- Reports two valid rows and four invalid rows.
- Reports one issue for each validation rule.
- Returns exit code `7`.

Observed result:

```text
Total rows: 6
Valid rows: 2
Invalid rows: 4

Validation issues:
- invalid_event_id: 1
- invalid_time_created: 1
- empty_target_user_name: 1
- invalid_ip_address: 1
Result: FAIL
Exit code: 7
```

Status: PASS

## Test 2 - Valid Normalized CSV

Command:

```powershell
python .\src\main.py --input .\sample-output\messy-events.normalized.csv --validate-fields
```

Expected behavior:

- Detects two valid rows.
- Reports no validation issues.
- Returns exit code `0`.

Observed result:

```text
Total rows: 2
Valid rows: 2
Invalid rows: 0

Validation issues:
- none
Result: PASS
Exit code: 0
```

Status: PASS

## Test 3 - Strict Timestamp Format

Command:

```powershell
python .\src\main.py --input .\sample-data\timestamp-format-edge.csv --validate-fields
```

Test data contains this non-compliant timestamp:

```text
2026-7-05T13:00:00Z
```

Expected behavior:

- Rejects the timestamp because the month does not use two digits.
- Reports one `invalid_time_created` issue.
- Returns exit code `7`.

Observed result:

```text
Total rows: 1
Valid rows: 0
Invalid rows: 1

Validation issues:
- invalid_event_id: 0
- invalid_time_created: 1
- empty_target_user_name: 0
- invalid_ip_address: 0
Result: FAIL
Exit code: 7
```

Status: PASS

## Test 4 - Raw Schema Is Rejected

Command:

```powershell
python .\src\main.py --input .\sample-data\valid-events.csv --validate-fields
```

Expected behavior:

- Rejects the raw schema because it does not contain normalized headers.
- Returns exit code `4`.

Observed result:

```text
Missing columns: event_id, time_created, target_user_name, ip_address
Result: FAIL
Exit code: 4
```

Status: PASS

## Test 5 - Output Guard for Read-Only Mode

Command:

```powershell
python .\src\main.py `
  --input .\sample-output\messy-events.normalized.csv `
  --validate-fields `
  --output .\sample-output\phase5-unexpected-output.csv
```

Expected behavior:

- Rejects `--output` because it is only valid with `--normalize-csv`.
- Returns exit code `6`.
- Does not create an output file.

Observed result:

```text
ERROR: --output is only supported when using --normalize-csv.
Exit code: 6
Test-Path .\sample-output\phase5-unexpected-output.csv
False
```

Status: PASS

## Test 6 - Input Integrity

Command:

```powershell
$beforeHash = (Get-FileHash .\sample-data\normalized-field-validation.csv -Algorithm SHA256).Hash

python .\src\main.py `
  --input .\sample-data\normalized-field-validation.csv `
  --validate-fields

$exitCode = $LASTEXITCODE
$afterHash = (Get-FileHash .\sample-data\normalized-field-validation.csv -Algorithm SHA256).Hash

Write-Host "Input hash unchanged:" ($beforeHash -eq $afterHash)
Write-Host "Exit code:" $exitCode
```

Expected behavior:

- The input hash remains unchanged.
- Returns exit code `7` because the sample contains intentional invalid values.

Observed result:

```text
Input hash unchanged: True
Exit code: 7
```

Status: PASS

## Test 7 - Mutually Exclusive Modes

Command:

```powershell
python .\src\main.py `
  --input .\sample-data\normalized-field-validation.csv `
  --validate-csv `
  --validate-fields
```

Expected behavior:

- `argparse` rejects the conflicting modes.
- Returns exit code `2`.

Observed result:

```text
main.py: error: argument --validate-fields: not allowed with argument --validate-csv
Exit code: 2
```

Status: PASS

## Security Notes

- All files are sanitized samples.
- `--validate-fields` is read-only and does not create output files.
- Input integrity was verified using SHA-256 before and after validation.
- The tool does not delete, move, upload, or execute input files.
- No credentials, customer data, production logs, or internal infrastructure identifiers are included.

## Limitations

- Only normalized CSV input is supported.
- No output report file is created; results are printed to the terminal only.
- No row-level report identifies which row contained each issue.
- IPv6 is intentionally rejected.
- No event correlation, detection logic, alerting, or MITRE mapping exists yet.
- No automated test suite exists yet.

## Next Step

Build MVP 05: produce a safe row-level validation report for invalid rows without changing the source input.
