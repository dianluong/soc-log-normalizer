# Copilot Instructions — SOC Log Normalizer

## Project Purpose

This repository is a learning project for SOC and security automation.

The goal is to build a small Python CLI tool that reads CSV or JSON log exports, validates records, normalizes key fields, and writes a safe output file for analysis.

The code must be understandable, testable, and suitable for a public GitHub portfolio.

## Coding Expectations

- Use Python 3.10-compatible code.
- Prefer simple functions over complex abstractions.
- Use clear function names, docstrings, and type hints where useful.
- Use `argparse` for command-line arguments.
- Validate input paths, file types, required fields, and malformed JSON or CSV rows.
- Handle errors explicitly and show useful error messages.
- Use the standard library first. Add external dependencies only when necessary.
- Do not silently ignore exceptions.
- Add logging when processing multiple records or files.
- Keep the first version as a small MVP before adding advanced features.

## Security and Privacy

- Never hardcode passwords, tokens, IP addresses, usernames, customer data, or private paths.
- Treat all log input as untrusted data.
- Do not execute commands, scripts, or file paths found inside log fields.
- Do not commit real production logs.
- Use sanitized sample data only.
- Keep `.env`, `*.log`, virtual environments, and cache files out of Git.

## Project Structure

- `src/` contains application code.
- `tests/` contains automated tests.
- `sample-data/` contains sanitized input samples only.
- `docs/` contains diagrams, notes, and evidence.
- `README.md` explains purpose, setup, usage, validation, and limitations.

## Teaching Style

When suggesting code:

1. State what problem the change solves.
2. Explain the important logic briefly.
3. Provide a command to run or test it.
4. State expected output.
5. Include one likely failure case and how to debug it.

Do not generate a large finished tool without first establishing a small working version.