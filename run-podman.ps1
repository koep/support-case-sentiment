# PowerShell script to run the CSV chunking tool in Podman

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ImageName = "csv-to-notebooklm"

Write-Host "Building Podman image: $ImageName"
podman build -t $ImageName $ScriptDir

Write-Host ""
Write-Host "Running container to process CSV files..."
Write-Host "Output will be saved to: $ScriptDir\notebooklm_chunks"
Write-Host ""

podman run --rm `
  -v "${ScriptDir}:/app/data" `
  -w /app/data `
  $ImageName python3 chunk_csv_for_notebooklm.py

Write-Host ""
Write-Host "Processing complete!"
Write-Host "Check the notebooklm_chunks/ directory for output files."
