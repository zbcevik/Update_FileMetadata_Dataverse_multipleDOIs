# Examples and Use Cases

This document provides practical examples for different scenarios.

## Example 1: Basic Metadata Update

Scenario: Update descriptions for three datasets

### Setup

```bash
# Activate environment
source venv/bin/activate

# Create directories
mkdir -p data/json_templates
```

### Process

```bash
# Step 1: Convert JSON to CSV
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/metadata.csv

# Step 2: Edit data/metadata.csv
# - Open in Excel or Google Sheets
# - Update "new_description" column for each file
# - Save

# Step 3: Convert back to JSON
python csv_to_json.py \
    --csv-file ./data/metadata.csv \
    --output-dir ./data/json_output

# Step 4: Push to Dataverse
export DATAVERSE_SERVER_URL="https://dataverse.org"
export DATAVERSE_API_TOKEN="your-token"

python dataverse_api.py \
    --csv-file ./data/metadata.csv \
    --no-dry-run
```

---

## Example 2: Reorganize File Paths

Scenario: Move files to different directory structure

### CSV Changes

Before:
```
DOI | file_label | file_path | new_file_path
--- | ---------- | --------- | ---------------
doi:10.5061/example1 | data.csv | raw_data | 
doi:10.5061/example1 | report.pdf | outputs |
```

After:
```
DOI | file_label | file_path | new_file_path
--- | ---------- | --------- | ----------------
doi:10.5061/example1 | data.csv | raw_data | 2024/raw_data
doi:10.5061/example1 | report.pdf | outputs | 2024/processed
```

### Commands

```bash
# Update CSV with new paths
python csv_to_json.py --csv-file ./data/metadata.csv

# Preview changes
python dataverse_api.py --csv-file ./data/metadata.csv

# Apply changes
python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run
```

---

## Example 3: Bulk Update Multiple Datasets

Scenario: Update 10 datasets in one batch

### Setup

```bash
# Prepare JSON files
ls data/json_templates/
# dataset1.json, dataset2.json, ..., dataset10.json

# All files will be processed by default
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/bulk_metadata.csv
```

### Process

```bash
# CSV will have 50+ rows (multiple files per dataset)
wc -l data/bulk_metadata.csv
# 51 data/bulk_metadata.csv (header + 50 files)

# Edit all descriptions in bulk
# (Use search/replace in spreadsheet editor)

# Convert and push
python csv_to_json.py --csv-file ./data/bulk_metadata.csv

python dataverse_api.py \
    --csv-file ./data/bulk_metadata.csv \
    --no-dry-run
```

---

## Example 4: Update Only Specific Files

Scenario: Update only 5 files out of 20

### CSV Preparation

```bash
# Generate full CSV
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/metadata.csv

# Manually delete rows you don't want to update
# Or set their status to "skip"

# Save as new file
cp data/metadata.csv data/partial_update.csv
# Edit data/partial_update.csv and remove unwanted rows
```

### Process

```bash
# Only selected files will be updated
python csv_to_json.py --csv-file ./data/partial_update.csv

python dataverse_api.py \
    --csv-file ./data/partial_update.csv \
    --no-dry-run
```

---

## Example 5: Scheduled Bulk Updates

Scenario: Automatically update datasets monthly

### Create Cron Script

```bash
#!/bin/bash
# File: update_datasets.sh

cd /path/to/project
source venv/bin/activate

# Set credentials
export DATAVERSE_SERVER_URL="https://dataverse.org"
export DATAVERSE_API_TOKEN="your-token"

# Run update workflow
python json_to_csv.py --input-dir ./data/json_templates
python csv_to_json.py --csv-file ./data/metadata.csv
python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run

# Log the result
echo "Update completed: $(date)" >> logs/scheduled_updates.log
```

### Schedule with Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2 AM on the 1st of every month)
0 2 1 * * /path/to/project/update_datasets.sh

# Verify
crontab -l
```

---

## Example 6: Version Control Integration

Scenario: Track all metadata changes in Git

### Process

```bash
# Initial commit
git add data/json_templates/
git add data/metadata.csv
git add *.py
git commit -m "Initial metadata for 3 datasets"

# Later, make changes
python json_to_csv.py --input-dir ./data/json_templates

# See what changed
git diff data/metadata.csv

# Review specific changes
git diff data/metadata.csv | head -50

# Commit changes
git add data/metadata.csv
git commit -m "Updated descriptions for 8 files

- Climate dataset: Added quality control info
- Survey dataset: Added year range info
- Genomic dataset: Added platform specs"

# View history
git log --oneline data/metadata.csv

# Revert if needed
git checkout HEAD~1 -- data/metadata.csv
```

---

## Example 7: Custom Python Script

Scenario: Programmatically update descriptions with Python

```python
#!/usr/bin/env python3
# File: custom_update.py

from utils import load_csv_file, save_csv_file, load_json_file

# Load CSV
rows = load_csv_file('data/metadata.csv')

# Modify descriptions programmatically
for row in rows:
    if 'climate' in row.get('dataset_name', '').lower():
        if not row.get('new_description'):
            row['new_description'] = row.get('file_description', '') + ' [Climate data 2024]'
    
    elif 'survey' in row.get('dataset_name', '').lower():
        if not row.get('new_description'):
            row['new_description'] = row.get('file_description', '') + ' [Survey results]'

# Save updated CSV
fieldnames = [
    'DOI', 'dataset_name', 'file_id', 'file_label', 
    'file_description', 'file_path', 'file_size', 'file_type',
    'original_description', 'new_description', 'new_file_path', 'status'
]
save_csv_file(rows, 'data/metadata_updated.csv', fieldnames)

print(f"Updated {len(rows)} rows")
```

Run it:
```bash
python custom_update.py
```

---

## Example 8: Filter and Extract

Scenario: Export only specific dataset DOIs to separate CSV

```bash
#!/bin/bash
# File: extract_dataset.sh

DOI="doi:10.5061/dryad.example1"

# Extract rows matching DOI
grep "$DOI" data/metadata.csv > data/single_dataset.csv

# Add header back
head -1 data/metadata.csv | cat - data/single_dataset.csv > temp && mv temp data/single_dataset.csv

# Now process just this dataset
python csv_to_json.py --csv-file ./data/single_dataset.csv
```

---

## Example 9: Error Recovery

Scenario: Handle API errors gracefully

```python
#!/usr/bin/env python3
# File: safe_update.py

from dataverse_api import DataverseAPI, push_updates_from_csv
import sys
import logging

# Set up logging
logging.basicConfig(
    filename='logs/updates.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    # Test connection first
    api = DataverseAPI(
        "https://dataverse.org",
        "your-token"
    )
    
    if not api.test_connection():
        print("✗ Cannot connect to Dataverse")
        sys.exit(1)
    
    # Safe push with error handling
    push_updates_from_csv(
        'data/metadata.csv',
        'https://dataverse.org',
        'your-token',
        dry_run=False
    )
    
    logging.info("✓ Update completed successfully")
    
except Exception as e:
    logging.error(f"✗ Error: {str(e)}")
    print(f"Error occurred: {str(e)}")
    sys.exit(1)
```

---

## Example 10: Batch Processing

Scenario: Process multiple CSV files sequentially

```bash
#!/bin/bash
# File: batch_process.sh

for csv_file in data/batch_*.csv; do
    echo "Processing: $csv_file"
    
    # Convert to JSON
    python csv_to_json.py --csv-file "$csv_file"
    
    # Push to Dataverse
    python dataverse_api.py --csv-file "$csv_file" --no-dry-run
    
    # Log completion
    echo "  ✓ Complete"
done

echo "All batches processed"
```

Run it:
```bash
chmod +x batch_process.sh
./batch_process.sh
```

---

## Troubleshooting Examples

### Issue: CSV has wrong encoding

```python
# Fix encoding
import pandas as pd

df = pd.read_csv('data/metadata.csv', encoding='latin-1')
df.to_csv('data/metadata_fixed.csv', encoding='utf-8', index=False)
```

### Issue: API rate limiting

```bash
# Add delays between updates
python -c "
import time
from utils import load_csv_file
from dataverse_api import DataverseAPI

api = DataverseAPI('https://dataverse.org', 'token')
rows = load_csv_file('data/metadata.csv')

for row in rows:
    # Process each row
    time.sleep(1)  # 1 second delay between updates
    print(f\"Updated: {row['file_id']}\")
"
```

### Issue: Large CSV file performance

```python
# Process in chunks
import csv

chunk_size = 50
rows = []

with open('data/metadata.csv', 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        rows.append(row)
        if (i + 1) % chunk_size == 0:
            # Process chunk
            print(f"Processing chunk: rows {i-chunk_size+1}-{i+1}")
            rows = []
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Convert JSON to CSV | `python json_to_csv.py --input-dir ./data/json_templates` |
| Convert CSV to JSON | `python csv_to_json.py --csv-file ./data/metadata.csv` |
| Preview Dataverse changes | `python dataverse_api.py --csv-file ./data/metadata.csv` |
| Apply Dataverse changes | `python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run` |
| Single file conversion | `python json_to_csv.py --json-file ./data/json_templates/file.json` |
| Validate JSON format | `python -m json.tool < data/json_templates/file.json` |
| View CSV headers | `head -1 data/metadata.csv` |
| Count CSV rows | `wc -l data/metadata.csv` |
| Backup original | `cp -r data/json_templates data/json_templates.bak` |
| Restore backup | `cp -r data/json_templates.bak data/json_templates` |
