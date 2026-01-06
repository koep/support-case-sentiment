#!/usr/bin/env python3
"""
Convert CSV files to NotebookLM-compatible text chunks.

This script processes monthly CSV files containing case comments and converts them
into text files that comply with NotebookLM's limits:
- Max 200 MB per source
- Max 500,000 words per source
"""

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required but not installed.")
    print("Please install it using: pip install pandas")
    print("Or install all requirements: pip install -r requirements.txt")
    exit(1)

import json
import os
from pathlib import Path
from typing import List, Dict, Tuple
import re


# NotebookLM limits
MAX_WORDS_PER_CHUNK = 400000  # Safety margin below 500k limit
MAX_SIZE_MB_PER_CHUNK = 150  # Safety margin below 200MB limit
MAX_SIZE_BYTES_PER_CHUNK = MAX_SIZE_MB_PER_CHUNK * 1024 * 1024


def count_words(text: str) -> int:
    """Count words in text (simple whitespace-based counting)."""
    if not text or pd.isna(text):
        return 0
    # Remove extra whitespace and split
    words = re.findall(r'\b\w+\b', str(text))
    return len(words)


def format_entry(row: pd.Series) -> str:
    """Format a single CSV row as a readable text entry."""
    account = str(row['Account Name: Account Name']) if pd.notna(row['Account Name: Account Name']) else 'N/A'
    comment_num = str(row['Case Comment Number']) if pd.notna(row['Case Comment Number']) else 'N/A'
    case_num = str(row['Case Number']) if pd.notna(row['Case Number']) else 'N/A'
    location = str(row['Case Comment CreatedBy Location']) if pd.notna(row['Case Comment CreatedBy Location']) else 'N/A'
    comment_body = str(row['Comment Body']) if pd.notna(row['Comment Body']) else ''
    
    entry = f"""=== Case Comment: {comment_num} ===
Account: {account}
Case Number: {case_num}
Location: {location}
Comment:
{comment_body}

---
"""
    return entry


def create_chunk_header(source_file: str, start_row: int, end_row: int, total_rows: int) -> str:
    """Create header for a text chunk."""
    return f"""# Case Comments from {source_file}
# Rows: {start_row + 1} to {end_row + 1} of {total_rows}
# Generated for NotebookLM

"""


def process_csv_file(csv_path: Path, output_dir: Path) -> List[Dict]:
    """Process a single CSV file and create text chunks."""
    print(f"Processing {csv_path.name}...")
    
    # Read CSV file - try multiple encodings
    encodings = ['utf-8', 'iso-8859-1', 'latin-1', 'cp1252', 'windows-1252']
    df = None
    
    for encoding in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=encoding)
            if encoding != 'utf-8':
                print(f"  Using encoding: {encoding}")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
        except Exception as e:
            print(f"  Error with encoding {encoding}: {e}")
            continue
    
    if df is None:
        print(f"  ERROR: Could not read {csv_path.name} with any supported encoding")
        return []
    
    total_rows = len(df)
    print(f"  Total rows: {total_rows:,}")
    
    chunks_metadata = []
    chunk_num = 1
    current_chunk_rows = []
    current_chunk_words = 0
    current_chunk_size = 0
    start_row_idx = 0
    
    base_name = csv_path.stem  # e.g., "2025-01-germany-case-comments"
    
    for idx, row in df.iterrows():
        entry_text = format_entry(row)
        entry_words = count_words(entry_text)
        entry_size = len(entry_text.encode('utf-8'))
        
        # Check if adding this entry would exceed limits
        would_exceed_words = (current_chunk_words + entry_words) > MAX_WORDS_PER_CHUNK
        would_exceed_size = (current_chunk_size + entry_size) > MAX_SIZE_BYTES_PER_CHUNK
        
        # If this is the first entry or we'd exceed limits, save current chunk and start new one
        if current_chunk_rows and (would_exceed_words or would_exceed_size):
            # Save current chunk
            chunk_filename = f"{base_name}-part-{chunk_num:02d}.txt" if chunk_num > 1 or total_rows > len(current_chunk_rows) else f"{base_name}.txt"
            chunk_path = output_dir / chunk_filename
            
            chunk_text = create_chunk_header(csv_path.name, start_row_idx, idx - 1, total_rows)
            chunk_text += "".join([format_entry(df.iloc[i]) for i in current_chunk_rows])
            
            # Write chunk to file
            with open(chunk_path, 'w', encoding='utf-8') as f:
                f.write(chunk_text)
            
            # Calculate actual stats
            actual_words = count_words(chunk_text)
            actual_size = os.path.getsize(chunk_path)
            
            chunks_metadata.append({
                'filename': chunk_filename,
                'source_file': csv_path.name,
                'start_row': start_row_idx + 1,
                'end_row': idx,
                'row_count': len(current_chunk_rows),
                'word_count': actual_words,
                'size_bytes': actual_size,
                'size_mb': round(actual_size / (1024 * 1024), 2)
            })
            
            print(f"  Created chunk {chunk_num}: {chunk_filename} ({len(current_chunk_rows):,} rows, {actual_words:,} words, {actual_size / (1024*1024):.2f} MB)")
            
            # Start new chunk
            current_chunk_rows = []
            current_chunk_words = 0
            current_chunk_size = 0
            start_row_idx = idx
            chunk_num += 1
        
        # Add entry to current chunk
        current_chunk_rows.append(idx)
        current_chunk_words += entry_words
        current_chunk_size += entry_size
    
    # Save final chunk
    if current_chunk_rows:
        chunk_filename = f"{base_name}-part-{chunk_num:02d}.txt" if chunk_num > 1 else f"{base_name}.txt"
        chunk_path = output_dir / chunk_filename
        
        chunk_text = create_chunk_header(csv_path.name, start_row_idx, total_rows - 1, total_rows)
        chunk_text += "".join([format_entry(df.iloc[i]) for i in current_chunk_rows])
        
        with open(chunk_path, 'w', encoding='utf-8') as f:
            f.write(chunk_text)
        
        actual_words = count_words(chunk_text)
        actual_size = os.path.getsize(chunk_path)
        
        chunks_metadata.append({
            'filename': chunk_filename,
            'source_file': csv_path.name,
            'start_row': start_row_idx + 1,
            'end_row': total_rows,
            'row_count': len(current_chunk_rows),
            'word_count': actual_words,
            'size_bytes': actual_size,
            'size_mb': round(actual_size / (1024 * 1024), 2)
        })
        
        print(f"  Created chunk {chunk_num}: {chunk_filename} ({len(current_chunk_rows):,} rows, {actual_words:,} words, {actual_size / (1024*1024):.2f} MB)")
    
    return chunks_metadata


def validate_chunks(chunks_metadata: List[Dict]) -> Tuple[bool, List[str]]:
    """Validate that all chunks meet NotebookLM requirements."""
    errors = []
    warnings = []
    
    for chunk in chunks_metadata:
        # Check word count
        if chunk['word_count'] > 500000:
            errors.append(f"{chunk['filename']}: Exceeds 500k word limit ({chunk['word_count']:,} words)")
        elif chunk['word_count'] > 450000:
            warnings.append(f"{chunk['filename']}: Close to word limit ({chunk['word_count']:,} words)")
        
        # Check file size
        if chunk['size_mb'] > 200:
            errors.append(f"{chunk['filename']}: Exceeds 200MB limit ({chunk['size_mb']} MB)")
        elif chunk['size_mb'] > 180:
            warnings.append(f"{chunk['filename']}: Close to size limit ({chunk['size_mb']} MB)")
    
    return len(errors) == 0, errors + warnings


def main():
    """Main execution function."""
    # Use current working directory (works in both host and container)
    work_dir = Path.cwd()
    csv_files = sorted(work_dir.glob("2025-*-germany-case-comments.csv"))
    
    if not csv_files:
        print("No CSV files found matching pattern '2025-*-germany-case-comments.csv'")
        print(f"Current directory: {work_dir}")
        return
    
    print(f"Found {len(csv_files)} CSV files to process\n")
    
    # Create output directory
    output_dir = work_dir / "notebooklm_chunks"
    output_dir.mkdir(exist_ok=True)
    print(f"Output directory: {output_dir}\n")
    
    all_chunks_metadata = []
    
    # Process each CSV file
    for csv_file in csv_files:
        chunks_meta = process_csv_file(csv_file, output_dir)
        all_chunks_metadata.extend(chunks_meta)
        print()
    
    # Generate metadata.json
    metadata = {
        'total_chunks': len(all_chunks_metadata),
        'total_rows': sum(chunk['row_count'] for chunk in all_chunks_metadata),
        'total_words': sum(chunk['word_count'] for chunk in all_chunks_metadata),
        'total_size_mb': round(sum(chunk['size_mb'] for chunk in all_chunks_metadata), 2),
        'chunks': all_chunks_metadata
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    print(f"Metadata saved to {metadata_path}")
    print(f"\nSummary:")
    print(f"  Total chunks created: {len(all_chunks_metadata)}")
    print(f"  Total rows processed: {metadata['total_rows']:,}")
    print(f"  Total words: {metadata['total_words']:,}")
    print(f"  Total size: {metadata['total_size_mb']} MB")
    
    # Validate chunks
    print("\nValidating chunks...")
    is_valid, messages = validate_chunks(all_chunks_metadata)
    
    if messages:
        for msg in messages:
            if "Exceeds" in msg:
                print(f"  ERROR: {msg}")
            else:
                print(f"  WARNING: {msg}")
    
    if is_valid:
        print("\n✓ All chunks are within NotebookLM limits!")
    else:
        print("\n✗ Some chunks exceed NotebookLM limits. Please review.")
    
    print(f"\nChunks are ready in: {output_dir}")


if __name__ == "__main__":
    main()

