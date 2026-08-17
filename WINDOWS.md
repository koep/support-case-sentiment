# Running on Windows

This guide covers installing Git and Podman on Windows, cloning the repository, and running the CSV-to-NotebookLM conversion tool.

## Install Git

1. Download the installer from [git-scm.com/downloads/win](https://git-scm.com/downloads/win)
2. Run the installer. The defaults work for most users. Two settings worth checking:
   - **Default editor**: Choose your preferred editor (VS Code, Notepad++, etc.)
   - **Line ending conversions**: Select **"Checkout as-is, commit Unix-style line endings"** to avoid CRLF issues with the Dockerfile
3. Open **PowerShell** and verify:

```powershell
git --version
```

## Install Podman

Podman Desktop provides both the container engine and a graphical management interface.

1. Download **Podman Desktop** from [podman-desktop.io](https://podman-desktop.io/)
2. Run the installer
3. Launch Podman Desktop after installation
4. On first launch, Podman Desktop will prompt you to install the **Podman engine** if it is not already present — follow the guided setup
5. Initialize and start a Podman machine. Podman Desktop walks you through this, or do it from PowerShell:

```powershell
podman machine init
podman machine start
```

6. Verify Podman is working:

```powershell
podman --version
podman run --rm hello-world
```

> **Note:** Podman on Windows runs containers inside a Linux VM (the "Podman machine"). The machine must be running before you can build or run containers. If you see connection errors, run `podman machine start`.

## Clone the repository

```powershell
git clone <repository-url>
cd support-case-sentiment
```

## Place your CSV files

Copy your Salesforce CSV exports into the project root directory (the folder containing `chunk_csv_for_notebooklm.py`). No naming convention required — see the main [README](README.md).

## Run with the PowerShell script

A dedicated `run-podman.ps1` script is included for Windows. Open PowerShell in the project directory and run:

```powershell
.\run-podman.ps1
```

This will:

1. Build a Podman container image with Python and pandas
2. Run the container to process matching CSV files in the current directory
3. Save output to `notebooklm_chunks/` on your host
4. Clean up the container automatically

### PowerShell execution policy

If PowerShell blocks the script with a security error, allow it for the current session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\run-podman.ps1
```

## Manual Podman commands

If you prefer to run the commands directly:

```powershell
# Build the container image
podman build -t csv-to-notebooklm .

# Run the container
podman run --rm -v "${PWD}:/app/data" -w /app/data csv-to-notebooklm
```

## Output

After running, you will find:

- `notebooklm_chunks/*.txt` — Text files ready for upload to NotebookLM
- `notebooklm_chunks/metadata.json` — Chunk statistics (row counts, word counts, file sizes)
- `notebooklm_chunks/README.md` — Upload instructions

## Troubleshooting

### "podman: command not found"

Podman CLI is not in your PATH. Restart your terminal after installing Podman Desktop. If the issue persists, reinstall Podman Desktop and ensure the option to add Podman to PATH is checked.

### Cannot connect to Podman / machine not running

```powershell
podman machine start
```

### Container cannot find CSV files

Make sure you are running the command from the project directory. In PowerShell, use `${PWD}` for the volume mount path (not `$(pwd)`, which is Bash syntax).

### Script error: `python3\r: No such file or directory`

Git checked out files with Windows-style line endings (CRLF). Fix by reconfiguring Git and re-cloning:

```powershell
git config --global core.autocrlf input
```

Then delete the project folder and clone again.

### Alternative: Run without Podman

If you cannot use Podman, install Python directly:

1. Download Python 3.11+ from [python.org/downloads](https://www.python.org/downloads/)
2. During installation, check **"Add Python to PATH"**
3. Open PowerShell in the project directory:

```powershell
pip install -r requirements.txt
python chunk_csv_for_notebooklm.py
```
