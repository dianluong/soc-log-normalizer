# MVP 03 Verification - CSV Field Normalization

## Objective

Verify that `src/main.py` can normalize a validated sanitized CSV into a new output file without modifying the input file.

## Input Schema

```text
EventID
TimeCreated
TargetUserName
IpAddress
```

## Normalized Output Schema

```text
event_id
time_created
target_user_name
ip_address
```

## Normalization Rules

- Rename source headers to the normalized output schema.
- Trim leading and trailing whitespace from field values.
- Preserve row order.
- Create a new output file only.
- Refuse to overwrite an existing output file.

## Test 1 - MVP 02 Regression

Command:

```powershell
python .\src\main.py --input .\sample-data\valid-events.csv --validate-csv
```

Expected behavior:

- Required columns are detected.
- Data row count is `2`.
- Exit code is `0`.

Observed result:

```text
Data rows: 2
Result: PASS
Exit code: 0
```

Status: PASS

## Test 2 - Successful Normalization

Command:

```powershell
python .\src\main.py --input .\sample-data\messy-events.csv --normalize-csv --output .\sample-output\messy-events.normalized.csv
```

Expected behavior:

- Input schema validation passes.
- A new normalized CSV is created.
- Output headers use normalized names.
- Whitespace is trimmed.
- Two rows are written.
- Exit code is `0`.

Observed result:

```text
Output columns: event_id, time_created, target_user_name, ip_address
Data rows written: 2
Result: PASS
Exit code: 0
```

Normalized output:

```text
event_id,time_created,target_user_name,ip_address
4625,2026-07-05T13:00:00Z,lab-user,192.0.2.10
4625,2026-07-05T13:05:00Z,lab-admin,192.0.2.11
```

Comparison result:

```text
Compare-Object returned no output.
```

Status: PASS

## Test 3 - Existing Output Protection

Command:

```powershell
python .\src\main.py --input .\sample-data\messy-events.csv --normalize-csv --output .\sample-output\messy-events.normalized.csv
```

Expected behavior:

- Existing output is not overwritten.
- Exit code is `6`.

Observed result:

```text
ERROR: Output path already exists and will not be overwritten: sample-output\messy-events.normalized.csv
Exit code: 6
```

The normalized file was compared with the expected file after the refusal. `Compare-Object` returned no output, confirming that the output file remained unchanged.

Status: PASS

## Test 4 - Missing Output Argument

Command:

```powershell
python .\src\main.py --input .\sample-data\messy-events.csv --normalize-csv
```

Expected behavior:

- Reports that `--output` is required.
- Exit code is `6`.

Observed result:

```text
ERROR: --output is required when using --normalize-csv.
Exit code: 6
```

Status: PASS

## Test 5 - Invalid Schema Does Not Create Output

Command:

```powershell
python .\src\main.py --input .\sample-data\missing-columns.csv --normalize-csv --output .\sample-output\invalid-schema.normalized.csv
```

Expected behavior:

- Reports missing required columns.
- Exit code is `4`.
- No output file is created.

Observed result:

```text
Missing columns: TargetUserName, IpAddress
Result: FAIL
Exit code: 4
Test-Path .\sample-output\invalid-schema.normalized.csv
False
```

Status: PASS

## Test 6 - Output Directory Does Not Exist

Command:

```powershell
python .\src\main.py --input .\sample-data\messy-events.csv --normalize-csv --output .\missing-output-dir\should-not-exist.csv
```

Expected behavior:

- Reports that the output directory does not exist.
- Returns exit code `6`.
- Does not create an output file.

Observed result:

```text
ERROR: Output directory does not exist: missing-output-dir
Exit code: 6
Test-Path .\missing-output-dir\should-not-exist.csv
False
```

Status: PASS

## Test 7 - Mutually Exclusive Modes

Command:

```powershell
python .\src\main.py --input .\sample-data\valid-events.csv --validate-csv --normalize-csv
```

Expected behavior:

- `argparse` rejects using both modes together.
- Returns exit code `2`.

Observed result:

```text
usage: main.py [-h] --input INPUT [--validate-csv | --normalize-csv] [--output OUTPUT]
main.py: error: argument --normalize-csv: not allowed with argument --validate-csv
Exit code: 2
```

Status: PASS

## Test 8 - Input Integrity

Command:

```powershell
$beforeHash = (Get-FileHash .\sample-data\messy-events.csv -Algorithm SHA256).Hash

python .\src\main.py `
  --input .\sample-data\messy-events.csv `
  --normalize-csv `
  --output .\sample-output\input-integrity-check.csv

$exitCode = $LASTEXITCODE
$afterHash = (Get-FileHash .\sample-data\messy-events.csv -Algorithm SHA256).Hash

Write-Host "Input hash unchanged:" ($beforeHash -eq $afterHash)
Write-Host "Exit code:" $exitCode
```

Expected behavior:

- The input file hash remains unchanged after normalization.
- A separate output file is created.
- Exit code is `0`.

Observed result:

```text
Input hash unchanged: True
Exit code: 0
```

The temporary output file was removed after verification.

Status: PASS

## Security Notes

- All input and output files are sanitized samples.
- The input CSV is never modified.
- The tool refuses to overwrite an existing output file.
- The tool does not delete, move, upload, or execute files.
- No credentials, PII, customer data, production logs, or internal infrastructure identifiers are included.

## Limitations

- Only CSV input is supported.
- Required source column names must match exactly.
- Values are trimmed but not semantically validated.
- Event IDs, timestamps, usernames, and IP addresses are not validated yet.
- No detection logic, aggregation, or report generation exists yet.
- No automated tests exist yet.

## Next Step

Build MVP 04: validate selected field values and produce a simple normalization summary report.
