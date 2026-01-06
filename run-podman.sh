#!/bin/bash
# Script to run the CSV chunking tool in Podman

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="csv-to-notebooklm"
CONTAINER_NAME="csv-chunker-$$"

echo "Building Podman image: $IMAGE_NAME"
podman build -t "$IMAGE_NAME" "$SCRIPT_DIR"

echo ""
echo "Running container to process CSV files..."
echo "Output will be saved to: $SCRIPT_DIR/notebooklm_chunks"
echo ""

# Run the container with volume mounts
# The :Z flag is for SELinux compatibility (can be removed if not needed)
podman run --rm \
  --name "$CONTAINER_NAME" \
  -v "$SCRIPT_DIR:/app/data:Z" \
  -w /app/data \
  "$IMAGE_NAME" python3 chunk_csv_for_notebooklm.py

echo ""
echo "✓ Processing complete!"
echo "Check the notebooklm_chunks/ directory for output files."

