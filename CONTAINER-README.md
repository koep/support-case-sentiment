# Running in Podman (No Host Installation Required)

This setup allows you to run the CSV chunking tool entirely in a Podman container, with no dependencies installed on your host system.

## Quick Start

Simply run:

```bash
./run-podman.sh
```

This will:
1. Build a Podman image with Python and pandas
2. Run the container to process all CSV files
3. Save output to `notebooklm_chunks/` directory on your host
4. Clean up the container automatically

## Manual Podman Commands

If you prefer to run commands manually:

### Build the image:
```bash
podman build -t csv-to-notebooklm .
```

### Run the container:
```bash
podman run --rm \
  -v "$(pwd):/app/data:Z" \
  -w /app/data \
  csv-to-notebooklm
```

The `-v` flag mounts your current directory into the container, so:
- CSV files are read from your host directory
- Output files are written back to your host `notebooklm_chunks/` directory

## What Gets Installed

**Nothing on your host!** Everything runs in the container:
- Python 3.11
- pandas library
- The conversion script

All dependencies are isolated in the container image.

## Output

After running, you'll find:
- `notebooklm_chunks/*.txt` - Text files ready for NotebookLM
- `notebooklm_chunks/metadata.json` - Chunk statistics
- `notebooklm_chunks/README.md` - Upload instructions

All files are created on your host system in the `notebooklm_chunks/` directory.

## Troubleshooting

### Permission Issues
If you encounter permission issues with the `:Z` flag on SELinux systems, you can remove it:
```bash
podman run --rm -v "$(pwd):/app/data" -w /app/data csv-to-notebooklm
```

### Rebuilding the Image
If you modify the script or requirements, rebuild:
```bash
podman build -t csv-to-notebooklm .
```

### Viewing Container Logs
The script output is displayed directly. If you need to debug:
```bash
podman run --rm -it -v "$(pwd):/app/data:Z" -w /app/data csv-to-notebooklm /bin/bash
```

