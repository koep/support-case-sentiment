FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
# (Script and CSV files will be mounted as volume)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Default command (can be overridden)
CMD ["python3", "chunk_csv_for_notebooklm.py"]

