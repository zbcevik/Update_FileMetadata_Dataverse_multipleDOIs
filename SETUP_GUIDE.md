# Quick Setup Guide

Get started in 5 minutes!

## Step 1: Install (2 minutes)

```bash
# Clone repository
git clone <repository-url>
cd Update_FileMetadata_Dataverse_multipleDOIs

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install requests
```

## Step 2: Prepare Your Data (1 minute)

Place your JSON files in `data/json_templates/`:

```bash
# Your JSON files should be like:
# data/json_templates/dataset1.json
# data/json_templates/dataset2.json
# data/json_templates/dataset3.json
```

## Step 3: Convert to CSV (1 minute)

```bash
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/metadata.csv
```

This creates `data/metadata.csv` with all your file metadata.

## Step 4: Edit and Convert Back (1 minute)

Open `data/metadata.csv` in Excel or Google Sheets:
- Edit `new_description` column with updated descriptions
- Edit `new_file_path` column if reorganizing files
- Save the file

```bash
# Convert back to JSON
python csv_to_json.py --csv-file ./data/metadata.csv
```

This creates updated JSON files in `data/json_output/`.

## Step 5: Push to Dataverse (Optional)

```bash
# Set credentials
export DATAVERSE_SERVER_URL="https://your-dataverse.org"
export DATAVERSE_API_TOKEN="your-api-token"

# First, preview changes
python dataverse_api.py --csv-file ./data/metadata.csv

# Then apply changes
python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run
```

## That's It!

Your metadata is now updated! For more details, see:
- `README.md` - Complete documentation
- `WORKFLOW.md` - Detailed workflow guide
- `INSTALLATION.md` - Installation help
- `EXAMPLES.md` - Practical examples

## Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| "json not found" | Place JSON files in `data/json_templates/` |
| Python errors | Run `pip install requests` |
| Dataverse connection fails | Check `DATAVERSE_SERVER_URL` and `DATAVERSE_API_TOKEN` |
| CSV issues | Ensure saved as UTF-8 encoding |

## Key Commands Reference

```bash
# JSON → CSV
python json_to_csv.py --input-dir ./data/json_templates

# CSV → JSON
python csv_to_json.py --csv-file ./data/metadata.csv

# Preview changes
python dataverse_api.py --csv-file ./data/metadata.csv

# Apply changes
python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run

# Get help
python json_to_csv.py --help
python csv_to_json.py --help
python dataverse_api.py --help
```

## File Structure

```
Project/
├── data/
│   ├── json_templates/          # Your JSON files (input)
│   ├── json_output/             # Generated JSON files (from CSV)
│   └── metadata.csv             # Edit this file
├── json_to_csv.py               # JSON → CSV
├── csv_to_json.py               # CSV → JSON
├── dataverse_api.py             # Dataverse API
├── README.md                    # Full documentation
└── WORKFLOW.md                  # Detailed workflow
```

Happy updating! 🎉
