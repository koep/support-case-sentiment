# Support Case Sentiment — CSV to NotebookLM

Converts monthly support case comment CSV exports into NotebookLM-compatible text chunks (under 200 MB and 500,000 words per file).

## Data year filter

The script currently processes only **2026** CSV files. In `chunk_csv_for_notebooklm.py`, the file glob is hardcoded:

```python
csv_files = sorted(work_dir.glob("2026-*-germany-case-comments.csv"))
```

To process a different year (for example 2025), change `2026` in that pattern to match your CSV filenames, then re-run the script.

## Data sensitivity

The CSV inputs and generated `notebooklm_chunks/` output can contain **personally identifiable information (PII)** and other sensitive support data, including:

- Customer and account names
- Case and comment identifiers
- Email addresses and personal names in comment bodies
- Internal support engineer names and locations

These data files are listed in `.gitignore` and are **not** committed to this repository. Only the conversion tooling is tracked in git. Do not commit CSV or chunk files, and treat any generated output as confidential.

## Quick Start (Podman)

No host Python installation required — run everything in a container:

```bash
./run-podman.sh
```

This will:

1. Build a Podman image with Python and pandas
2. Run the container to process matching CSV files in the current directory
3. Save output to `notebooklm_chunks/` on your host
4. Clean up the container automatically

## Manual Podman commands

### Build the image

```bash
podman build -t csv-to-notebooklm .
```

### Run the container

```bash
podman run --rm \
  -v "$(pwd):/app/data:Z" \
  -w /app/data \
  csv-to-notebooklm
```

The `-v` flag mounts your current directory into the container, so:

- CSV files are read from your host directory
- Output files are written back to your host `notebooklm_chunks/` directory

## What gets installed

**Nothing on your host.** Everything runs in the container:

- Python 3.11
- pandas
- The conversion script

All dependencies are isolated in the container image.

## Output

After running, you'll find:

- `notebooklm_chunks/*.txt` — Text files ready for NotebookLM
- `notebooklm_chunks/metadata.json` — Chunk statistics
- `notebooklm_chunks/README.md` — Upload instructions

All files are created on your host system in the `notebooklm_chunks/` directory.

## Troubleshooting

### Permission issues

If you encounter permission issues with the `:Z` flag on SELinux systems, you can remove it:

```bash
podman run --rm -v "$(pwd):/app/data" -w /app/data csv-to-notebooklm
```

### Rebuilding the image

If you modify the script or requirements, rebuild:

```bash
podman build -t csv-to-notebooklm .
```

### Viewing container logs

The script output is displayed directly. If you need to debug:

```bash
podman run --rm -it -v "$(pwd):/app/data:Z" -w /app/data csv-to-notebooklm /bin/bash
```
