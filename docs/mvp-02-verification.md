# MVP 02 Verification - CSV Schema Validation

## Objective

Verify that `src/main.py` can validate a sanitized CSV file before future log-normalization steps.

The validator checks:

- Input path exists.
- Input path is a file.
- Input extension is `.csv`.
- CSV header row exists.
- Required columns exist.
- Data-row count is reported.

## Required Columns

```text
EventID
TimeCreated
TargetUserName
IpAddress
```

## Test 1 - MVP 01 Regression

Command:

```powershell
python .\src\main.py --input .\sample-data\sample.txt
```

Expected behavior:

- Prints safe file metadata.
- Exit code is `0`.

Observed result:

```text
Input File Inspection
Path: C:\Users\User\Documents\GitHub\soc-log-normalizer\sample-data\sample.txt
Exists: True
Extension: .txt
Size (bytes): 40
Exit code: 0
```

Status: PASS

## Test 2 - Valid CSV With Data Rows

Command:

```powershell
python .\src\main.py --input .\sample-data\valid-events.csv --validate-csv
```

Expected behavior:

- Detects all required columns.
- Reports `2` data rows.
- Returns exit code `0`.

Observed result:

```text
Detected columns: EventID, TimeCreated, TargetUserName, IpAddress
Required columns: EventID, TimeCreated, TargetUserName, IpAddress
Data rows: 2
Result: PASS
Exit code: 0
```

Status: PASS

## Test 3 - CSV Missing Required Columns

Command:

```powershell
python .\src\main.py --input .\sample-data\missing-columns.csv --validate-csv
```

Expected behavior:

- Reports missing columns.
- Returns exit code `4`.

Observed result:

```text
Detected columns: EventID, TimeCreated
Missing columns: TargetUserName, IpAddress
Result: FAIL
Exit code: 4
```

Status: PASS

## Test 4 - Valid Schema With No Data Rows

Command:

```powershell
python .\src\main.py --input .\sample-data\empty-events.csv --validate-csv
```

Expected behavior:

- Confirms valid schema.
- Reports `0` data rows.
- Returns exit code `0`.

Observed result:

```text
Data rows: 0
Result: PASS (schema valid; no data rows)
Exit code: 0
```

Status: PASS

## Test 5 - Non-CSV Input

Command:

```powershell
python .\src\main.py --input .\sample-data\sample.txt --validate-csv
```

Expected behavior:

- Rejects non-CSV input.
- Returns exit code `3`.

Observed result:

```text
ERROR: CSV validation requires a .csv file: sample.txt
Exit code: 3
```

Status: PASS

## Test 6 - Missing File in CSV Mode

Command:

```powershell
python .\src\main.py --input .\sample-data\missing-events.csv --validate-csv
```

Expected behavior:

- Reports that the path does not exist.
- Returns exit code `1`.

Observed result:

```text
ERROR: Input path does not exist: sample-data\missing-events.csv
Exit code: 1
```

Status: PASS

## Security Notes

- All CSV files are sanitized sample data.
- The script reads CSV headers and counts rows only.
- The script does not normalize fields yet.
- The script does not modify, move, delete, or upload files.
- No credentials, customer data, production logs, or internal infrastructure identifiers are included.

## Limitations

- Only CSV is supported.
- Required columns must match exact names.
- CSV content values are not validated yet.
- Duplicate headers are not handled separately.
- No automated tests are implemented yet.
- No normalized output is generated yet.

## Next Step

Build MVP 03: normalize a validated CSV into a safe, consistent output schema.