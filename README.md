# Dataverse Bulk Metadata Update Tool

A comprehensive solution for managing and updating file metadata across multiple datasets in Dataverse instances. This tool allows you to convert between JSON and CSV formats, manage multiple DOIs, and perform bulk metadata updates.

## Features

✨ **Multi-Dataset Support**: Handle multiple datasets with different DOIs in a single workflow
📊 **CSV-Based Updates**: Edit metadata in a familiar spreadsheet format
🔄 **Bidirectional Conversion**: Convert between JSON and CSV formats seamlessly
🚀 **Bulk Operations**: Update metadata for multiple files across datasets at once
🔐 **API Integration**: Direct integration with Dataverse API for secure updates
📋 **Dry-Run Mode**: Preview changes before applying them to your datasets
📦 **Template System**: Work with JSON templates organized in convenient folder structure
🎯 **Tracking**: Track update status and changes for each file

## Project Structure

```
Update_FileMetadata_Dataverse_multipleDOIs/
├── utils.py                          # Utility functions for JSON/CSV operations
├── json_to_csv.py                    # Convert JSON files to CSV format
├── csv_to_json.py                    # Convert updated CSV back to JSON files
├── dataverse_api.py                  # Dataverse API interface for pushing updates
├── config.ini                        # Configuration file for settings
├── README.md                         # This file
├── WORKFLOW.md                       # Detailed workflow documentation
├── INSTALLATION.md                   # Installation and setup guide
├── data/
│   ├── json_templates/              # JSON template files for your datasets
│   │   ├── climate_data_2024.json
│   │   ├── genomic_data_species_a.json
│   │   └── survey_data_2024.json
│   ├── json_output/                 # Generated JSON files (after CSV updates)
│   └── metadata.csv                 # Main metadata file for editing
├── backups/                          # Automatic backups of original files
└── logs/                             # Operation logs

```

## Quick Start

### 1. Installation

```bash
# Clone or download the repository
cd Update_FileMetadata_Dataverse_multipleDOIs

# Install dependencies
pip install requests

# (Optional) Create a virtual environment first
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install requests
```

### 2. Basic Workflow

#### Step 1: Convert JSON to CSV

```bash
# Convert all JSON templates to CSV
python json_to_csv.py --input-dir ./data/json_templates --output-csv ./data/metadata.csv
```

This creates a CSV with columns:
- `DOI` - Dataset identifier
- `dataset_name` - Name of the dataset
- `file_id` - Unique file identifier
- `file_label` - File name/label
- `file_description` - Current description
- `file_path` - Current directory path
- `file_size` - File size in bytes
- `file_type` - Data type
- `original_description` - Original description (for reference)
- `new_description` - Update this column with new description
- `new_file_path` - Update this column with new file path
- `status` - Track update status

#### Step 2: Edit the CSV

Open `./data/metadata.csv` in your favorite spreadsheet editor (Excel, Google Sheets, etc.):

1. Review the current metadata
2. Edit the `new_description` column with updated descriptions
3. Edit the `new_file_path` column if file paths changed
4. Update the `status` column as needed

Example:
```
DOI                           | dataset_name | file_id | ... | original_description | new_description | status
doi:10.5061/dryad.example1   | Climate Data | file_001| ... | Old description     | Updated desc    | pending
```

#### Step 3: Convert CSV to JSON

```bash
# Convert your updated CSV back to JSON format
python csv_to_json.py --csv-file ./data/metadata.csv --output-dir ./data/json_output
```

This generates JSON files in `./data/json_output/` organized by DOI.

#### Step 4: Push to Dataverse (Optional)

```bash
# Set your credentials
export DATAVERSE_SERVER_URL="https://your-dataverse.org"
export DATAVERSE_API_TOKEN="your-api-token"

# First, do a dry run to preview changes
python dataverse_api.py --csv-file ./data/metadata.csv

# Apply changes to Dataverse
python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run
```

## Detailed Usage

### JSON to CSV Conversion

Convert one or more JSON files to CSV format:

```bash
# Convert all JSON files in directory
python json_to_csv.py \
    --input-dir ./data/json_templates \
    --output-csv ./data/metadata.csv

# Convert a single JSON file
python json_to_csv.py \
    --json-file ./data/json_templates/climate_data_2024.json \
    --output-csv ./data/single_dataset.csv
```

### CSV to JSON Conversion

Convert your edited CSV back to JSON files:

```bash
python csv_to_json.py \
    --csv-file ./data/metadata.csv \
    --output-dir ./data/json_output
```

### Push Updates to Dataverse

#### Prerequisites
- Dataverse instance with API access
- Valid API token with appropriate permissions
- Dataverse server URL

#### Dry Run Mode (Recommended First)

```bash
python dataverse_api.py \
    --csv-file ./data/metadata.csv \
    --server-url "https://your-dataverse.org" \
    --api-token "your-api-token"
```

This shows what changes would be made without actually applying them.

#### Apply Changes

```bash
python dataverse_api.py \
    --csv-file ./data/metadata.csv \
    --server-url "https://your-dataverse.org" \
    --api-token "your-api-token" \
    --no-dry-run
```

#### Using Environment Variables (More Secure)

```bash
export DATAVERSE_SERVER_URL="https://your-dataverse.org"
export DATAVERSE_API_TOKEN="your-api-token"

python dataverse_api.py --csv-file ./data/metadata.csv --no-dry-run
```

## JSON Template Format

Each JSON file should follow this structure:

```json
{
  "datasetPersistentId": "doi:10.5061/dryad.example",
  "datasetName": "Your Dataset Name",
  "dataset": {
    "version": 1,
    "releaseTime": "2024-01-15T10:00:00Z"
  },
  "data": [
    {
      "id": "file_001",
      "label": "filename.ext",
      "description": "File description",
      "directoryLabel": "folder_path",
      "filesize": 1024576,
      "dataType": "Text"
    }
  ],
  "lastUpdated": "2024-01-15T10:00:00Z"
}
```

### Key Fields

- `datasetPersistentId`: The DOI of your dataset (required)
- `datasetName`: Human-readable name of the dataset
- `data`: Array of file objects
  - `id`: Unique file identifier from Dataverse
  - `label`: File name or label
  - `description`: File description
  - `directoryLabel`: Directory path within the dataset
  - `filesize`: Size in bytes
  - `dataType`: File type (Text, Spreadsheet, Document, Sequence, etc.)

## CSV Work Columns

After converting JSON to CSV, you'll see these working columns:

| Column | Purpose |
|--------|---------|
| `DOI` | Dataset identifier (read-only) |
| `dataset_name` | Dataset name (read-only) |
| `file_id` | File ID (read-only) |
| `file_label` | File name (read-only) |
| `file_description` | Current description (read-only) |
| `original_description` | Reference copy (read-only) |
| `new_description` | **EDIT THIS** - New file description |
| `new_file_path` | **EDIT THIS** - New directory path |
| `status` | Update status tracking |

## Status Values

- `pending` - Changes ready to be applied
- `updated` - Changes successfully applied
- `no_changes` - No updates needed
- `error` - Error during update
- `skipped` - Update skipped

## Configuration

Edit `config.ini` to customize settings:

```ini
[dataverse]
server_url = https://your-dataverse.org
api_token = ${DATAVERSE_API_TOKEN}

[paths]
json_input_dir = ./data/json_templates
json_output_dir = ./data/json_output
csv_file = ./data/metadata.csv
```

## Examples

### Example 1: Update File Descriptions

1. Generate CSV from JSON files
2. Edit `new_description` column with better descriptions
3. Convert back to JSON
4. Push to Dataverse

### Example 2: Reorganize File Paths

1. Generate CSV from JSON files
2. Edit `new_file_path` column to reorganize files
3. Convert back to JSON
4. Push to Dataverse

### Example 3: Bulk Updates Across Multiple Datasets

1. Generate CSV from all JSON templates
2. Edit multiple datasets in one spreadsheet
3. Convert back to multiple JSON files
4. Push all updates with single command

## Troubleshooting

### Issue: "No JSON files found"
- **Solution**: Ensure JSON files are in `./data/json_templates` or specify correct path with `--input-dir`

### Issue: "CSV file not found"
- **Solution**: Ensure the CSV file path is correct and the file exists

### Issue: "Failed to connect to Dataverse"
- **Solution**: Check server URL and API token. Ensure server is accessible.

### Issue: "Status 401: Unauthorized"
- **Solution**: API token is invalid. Generate new token in your Dataverse account settings.

## Best Practices

1. **Always do a dry run first**: Review changes before applying
2. **Keep backups**: Original JSON files are preserved in `json_templates` directory
3. **Test with one dataset**: Before bulk updating, test with a single dataset
4. **Use version control**: Track your CSV changes with Git
5. **Log API token**: Set via environment variable, never hardcode
6. **Validate data**: Review CSV data before converting to JSON
7. **Document changes**: Update status column to track what was done

## Security Considerations

- **Never commit API tokens**: Use environment variables
- **Protect CSV files**: They contain file metadata which might be sensitive
- **Use HTTPS**: Ensure Dataverse connection is encrypted
- **Limit permissions**: Give API token only necessary permissions
- **Audit logs**: Enable logging to track all changes

## API Reference

### `utils.py`
- `load_json_file()` - Load JSON file
- `save_json_file()` - Save JSON file
- `load_csv_file()` - Load CSV file
- `save_csv_file()` - Save CSV file
- `extract_metadata_from_json()` - Extract metadata
- `validate_csv_row()` - Validate CSV row
- `get_json_files_from_directory()` - Get all JSON files from directory

### `json_to_csv.py`
- `json_to_csv_converter()` - Main conversion function

### `csv_to_json.py`
- `csv_to_json_converter()` - Main conversion function

### `dataverse_api.py`
- `DataverseAPI` - Dataverse API client class
- `push_updates_from_csv()` - Push updates to Dataverse

## Requirements

- Python 3.7+
- requests library (`pip install requests`)

## License

See LICENSE file for license information.

## Support

For issues or questions:
1. Check the TROUBLESHOOTING section above
2. Review WORKFLOW.md for detailed workflow documentation
3. Check INSTALLATION.md for setup help
4. Review log files in `./logs` for error details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Version History

- **v1.0** - Initial release with multi-DOI bulk update support