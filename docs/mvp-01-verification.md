# MVP 01 Verification — Safe Input File Inspection CLI

## Objective

Verify that `src/main.py` can safely inspect a local input file without reading, parsing, modifying, or uploading its contents.

## Command

```powershell
python .\src\main.py --input .\sample-data\sample.txt
```

## Valid Input Test

Input:

```text
sample-data\sample.txt
```

Expected behavior:

- Exit code is `0`.
- Prints the resolved file path.
- Prints `Exists: True`.
- Prints the file extension.
- Prints file size in bytes.

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

## Missing File Test

Command:

```powershell
python .\src\main.py --input .\sample-data\missing.txt
```

Expected behavior:

- Prints a clear error.
- Exit code is `1`.

Observed result:

```text
ERROR: Input path does not exist: sample-data\missing.txt
Exit code: 1
```

Status: PASS

## Directory Instead of File Test

Command:

```powershell
python .\src\main.py --input .\sample-data
```

Expected behavior:

- Prints a clear error.
- Exit code is `1`.

Observed result:

```text
ERROR: Input path is not a file: sample-data
Exit code: 1
```

Status: PASS

## Missing Required Argument Test

Command:

```powershell
python .\src\main.py
```

Expected behavior:

- `argparse` prints usage information.
- Exit code is `2`.

Observed result:

```text
usage: main.py [-h] --input INPUT
main.py: error: the following arguments are required: --input
Exit code: 2
```

Status: PASS

## Security Notes

- The script only reads file metadata through `Path.stat()`.
- The script does not open or parse file contents.
- The script does not modify, move, delete, or upload files.
- The sample input contains no real log data, credentials, PII, or infrastructure information.

## Limitations

- This MVP does not parse CSV, JSON, EVTX, or text logs.
- It does not validate file schema or content.
- It does not generate normalized output.
- It does not yet include automated tests.

## Next Step

Build MVP 02: validate a small sanitized CSV input schema before implementing log normalization.