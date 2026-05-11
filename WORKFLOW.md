# Detailed Workflow Guide

This document provides a step-by-step guide for the complete workflow of bulk updating metadata across multiple datasets.

## Workflow Overview

```
Step 1: JSON Templates          Step 2: CSV Generation       Step 3: Edit CSV
    ↓                               ↓                           ↓
  [ZIP or JSON files]    →    [json_to_csv.py]    →   [metadata.csv]
                                                         (Edit in Excel)
    ↑                                                       ↓
Step 8: Push Updates to       Step 7: Review JSON      Step 4: Convert
Dataverse                      Output Files           Back to JSON
    ↑                                                       ↓
    └────────────────────────────────┬────────────────────┘
                              Step 5-6: Generate JSON
                              [csv_to_json.py]
```

## Complete Step-by-Step Workflow

### Phase 1: Setup and Preparation

#### Step 1: Prepare JSON Templates

You have two options:

**Option A: Using existing JSON files**
```bash
# If you have JSON files, place them in data/json_templates/
mkdir -p data/json_templates
# Copy your JSON files here
cp path/to/your/json/files/* data/json_templates/
```

**Option B: Using a ZIP file**
```bash
# If you have a ZIP file with JSON files
unzip -d data/json_templates your_datasets.zip
```

**Option C: Create new JSON files**
Create JSON files following the template structure (see JSON Template Format section in README).

#### Step 2: Verify JSON Structure

```bash
# List all JSON files
ls -la data/json_templates/

# Check structure of a JSON file
cat data/json_templates/your_file.json | python -m json.tool
```

### Phase 2: Convert JSON to CSV

#### Step 3: Run JSON to CSV Conversion

```bash
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/metadata.csv
```

**Expected output:**
```
Processing: ./data/json_templates/climate_data_2024.json
Processing: ./data/json_templates/genomic_data_species_a.json
Processing: ./data/json_templates/survey_data_2024.json

Successfully converted 11 rows to ./data/metadata.csv
```

#### Step 4: Verify CSV Output

```bash
# View first 5 rows
head -5 data/metadata.csv

# Count total rows
wc -l data/metadata.csv

# View column headers
head -1 data/metadata.csv
```

### Phase 3: Edit Metadata

#### Step 5: Open CSV in Spreadsheet Editor

```bash
# Open with default application
open data/metadata.csv              # macOS
xdg-open data/metadata.csv          # Linux
start data/metadata.csv             # Windows
```

Or use an online editor like Google Sheets.

#### Step 6: Edit Metadata

For each row you want to update:

1. **Review the current data**
   - Check `original_description` column for context
   - Note the `file_label` to understand what file you're updating

2. **Fill in `new_description` column**
   ```
   Original: "Temperature data"
   New:      "Monthly average temperature data with quality control 
              applied, covering 2023-2024 period for North America"
   ```

3. **Fill in `new_file_path` column** (if reorganizing)
   ```
   Original: "raw_data"
   New:      "raw_data/v2"
   ```

4. **Update `status` column**
   - `pending` - To be updated
   - `no_changes` - Skip this row
   - `skip` - Ignore entirely

5. **Save the CSV file**

#### Step 7: Validation (Optional)

Create a validation script to check CSV before proceeding:

```python
#!/usr/bin/env python3
# validate_csv.py
import csv

with open('data/metadata.csv', 'r') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader, 1):
        # Check for required fields
        if not row['DOI']:
            print(f"Row {i}: Missing DOI")
        if not row['file_id']:
            print(f"Row {i}: Missing file_id")
        
        # Check for data in status field
        if row['status'] not in ['pending', 'no_changes', 'skip', 'updated']:
            print(f"Row {i}: Invalid status: {row['status']}")

print("Validation complete!")
```

Run it:
```bash
python validate_csv.py
```

### Phase 4: Convert Back to JSON

#### Step 8: Generate JSON Files from CSV

```bash
python csv_to_json.py \
    --csv-file ./data/metadata.csv \
    --output-dir ./data/json_output
```

**Expected output:**
```
✓ Created: ./data/json_output/doi_10_5061_dryad_example1.json
✓ Created: ./data/json_output/doi_10_5061_dryad_example2.json
✓ Created: ./data/json_output/doi_10_5061_dryad_example3.json

Successfully converted 3 JSON files to ./data/json_output
```

#### Step 9: Verify Generated JSON

```bash
# Check JSON validity
python -c "import json; json.load(open('data/json_output/doi_10_5061_dryad_example1.json'))" && echo "Valid JSON"

# View generated file structure
cat data/json_output/doi_10_5061_dryad_example1.json | python -m json.tool

# Compare with original
diff data/json_templates/climate_data_2024.json data/json_output/doi_10_5061_dryad_example1.json
```

### Phase 5: Push to Dataverse

#### Step 10: Configure Credentials

```bash
# Set environment variables
export DATAVERSE_SERVER_URL="https://dataverse.example.org"
export DATAVERSE_API_TOKEN="your-api-token-here"

# Or add to shell profile for persistence
echo 'export DATAVERSE_SERVER_URL="https://dataverse.example.org"' >> ~/.bashrc
echo 'export DATAVERSE_API_TOKEN="your-api-token-here"' >> ~/.bashrc
source ~/.bashrc
```

**Getting your API token:**
1. Go to Dataverse instance Settings → Account
2. Click "Create API Token"
3. Copy and save securely (never commit to version control)

#### Step 11: Test Connection

```bash
# Test if credentials are correct
python dataverse_api.py \
    --csv-file ./data/metadata.csv \
    --server-url "https://dataverse.example.org" \
    --api-token "your-token"
```

This runs in dry-run mode by default and shows what would be updated.

#### Step 12: Dry Run - Preview Changes

```bash
python dataverse_api.py \
    --csv-file ./data/metadata.csv
```

**Review output:**
```
============================================================
Dataset: doi:10.5061/dryad.example1
Files to update: 2

  File ID: file_001
  Label: temperature_data.csv
    Description: Monthly average... → Updated monthly average...
    ✓ Updated
    
  File ID: file_002
  Label: precipitation_analysis.xlsx
    Description: Precipitation patterns... → New analysis including...
    ✓ Updated

============================================================
DRY RUN: Would update 3 files
Use --no-dry-run to apply changes
```

#### Step 13: Apply Changes to Dataverse

```bash
# Apply the actual updates
python dataverse_api.py \
    --csv-file ./data/metadata.csv \
    --no-dry-run
```

**Verify changes in Dataverse:**
1. Go to each dataset in Dataverse web interface
2. Check that file descriptions and paths have been updated
3. Verify all files are still accessible

#### Step 14: Update CSV Status

After successful push, update the CSV `status` column:
- Change `pending` to `updated`
- Update `new_description` to blank (changes applied)
- Save as `./data/metadata_final.csv`

## Workflow Variations

### Variation 1: Single Dataset Update

Update only one dataset instead of multiple:

```bash
# Extract single dataset from CSV
# (or create new CSV with single dataset)

python csv_to_json.py \
    --csv-file ./data/single_dataset.csv \
    --output-dir ./data/json_output

python dataverse_api.py \
    --csv-file ./data/single_dataset.csv
```

### Variation 2: Incremental Updates

Track multiple update batches:

```bash
# First batch
python dataverse_api.py --csv-file ./data/batch1.csv --no-dry-run

# Second batch
python dataverse_api.py --csv-file ./data/batch2.csv --no-dry-run

# Track in version control
git add data/batch*.csv
git commit -m "Dataverse metadata updates - batches 1 and 2"
```

### Variation 3: Scheduled Updates

Create a cron job for regular updates:

```bash
# Add to crontab (monthly updates)
0 3 1 * * cd /path/to/project && python json_to_csv.py && \
          python csv_to_json.py --csv-file ./data/metadata.csv && \
          python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run
```

## Troubleshooting During Workflow

### Issue: JSON conversion produces empty CSV

**Solution:**
```bash
# Check if JSON files have correct structure
python -c "
import json
from utils import load_json_file

json_file = 'data/json_templates/your_file.json'
data = load_json_file(json_file)
print(f'DOI: {data.get(\"datasetPersistentId\")}')
print(f'Files: {len(data.get(\"data\", []))}')
"
```

### Issue: CSV has formatting errors

**Solution:**
```bash
# Validate CSV format
python -c "
import csv
with open('data/metadata.csv', 'r') as f:
    reader = csv.DictReader(f)
    print(f'Columns: {reader.fieldnames}')
    for i, row in enumerate(reader, 1):
        if i <= 3:
            print(f'Row {i}: {row}')
"
```

### Issue: JSON conversion loses data

**Solution:**
```bash
# Check what data is in each CSV row
python -c "
from utils import load_csv_file
rows = load_csv_file('data/metadata.csv')
for row in rows:
    if row['DOI']:
        print(f'{row[\"DOI\"]}: {len([v for v in row.values() if v])} fields filled')
"
```

### Issue: Dataverse API rejects updates

**Solution:**
```bash
# Check file IDs are valid
python -c "
from utils import load_csv_file
rows = load_csv_file('data/metadata.csv')
for row in rows[:3]:
    print(f'File ID: {row.get(\"file_id\")}, Label: {row.get(\"file_label\")}')
"
```

## Best Practices During Workflow

1. **Backup first**: Keep originals in git
   ```bash
   git add data/json_templates/*
   git commit -m "Backup original JSON files"
   ```

2. **Work in small batches**: Update 5-10 datasets at a time

3. **Review changes visually**: Always check Dataverse web interface after updates

4. **Keep audit trail**: Use git to track CSV changes
   ```bash
   git diff data/metadata.csv
   git add data/metadata.csv
   git commit -m "Updated descriptions for climate and survey datasets"
   ```

5. **Document changes**: Add notes in git commit messages
   ```
   git commit -m "Updated 8 file descriptions for improved clarity
   
   - Climate data: Added quality control info
   - Survey data: Added year range info
   - Genomic data: Added platform specification"
   ```

## Recovery and Rollback

If something goes wrong:

```bash
# Restore original JSON files
cp data/json_templates/* data/json_output/

# Revert CSV changes
git checkout data/metadata.csv

# Check git history
git log --oneline data/metadata.csv

# Restore previous version
git checkout HEAD~1 -- data/metadata.csv
```
