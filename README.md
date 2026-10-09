# Dataverse bulk file metadata updates

Update file descriptions and folder labels across multiple datasets using one spreadsheet.

**Dataset JSON files → CSV → edit → preview → apply**

This tool changes file metadata, not file contents. It does not publish datasets.

## Install and configure

Requires Python 3.9 or later.

The repository includes `config.sample.ini` as a configuration template. Copy it to `config.ini`, then enter your settings and API token in that local copy. Your private `config.ini` should not be uploaded to GitHub.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp config.sample.ini config.ini
```

On Windows, activate with `.venv\Scripts\activate` and copy the configuration using your file manager.

Edit `config.ini` to set your Dataverse HTTPS server URL, API token, JSON input directory, and CSV location. Paths are relative to the configuration file. Local configuration and generated CSV files are ignored by Git. Use a dedicated input directory for your own metadata; the bundled examples are fictional and must not be applied to a server.

## 1. Create the spreadsheet

Obtain dataset JSON exports from your Dataverse instance and place them in the configured input directory (one JSON file per dataset). This tool does not download exports.

```bash
python json_to_csv.py
```

Supported structures: flat `data` or `files` lists; `datasetVersion.files`; `latestVersion.files`; and dataset objects wrapped in an API `data` response. Nested `dataFile` objects are supported. A complete dataset DOI and positive numeric file IDs are required. Duplicate file IDs or invalid input stop conversion without producing a partial CSV.

An existing spreadsheet is protected against accidental replacement. To deliberately regenerate it after saving your edits elsewhere, use `python json_to_csv.py --overwrite`.

## 2. Edit the spreadsheet

Open the configured CSV in Excel or another spreadsheet editor. Save it as UTF-8 CSV.

| Column | Purpose |
| --- | --- |
| DOI, dataset_name | Dataset identity and title |
| file_id, file_label | File identity and name |
| original_description, file_path | Existing description and folder label |
| file_size, content_type, restricted, categories | Reference information |
| new_description | Enter a replacement description |
| new_file_path | Enter a replacement Dataverse folder label |

Edit only the two `new_` columns. Blank or whitespace-only cells mean **leave unchanged**; clearing a field is not supported. There is no status column. Remove rows or leave the new columns blank to exclude files. A nonblank value is an update request even if it matches the original.

## 3. Preview, then apply

```bash
python dataverse_api.py
```

Preview runs offline, requires no token, and displays only requested changes.

To apply, enter a token with permission to edit the datasets in your local `config.ini`:

```ini
[dataverse]
server_url = https://your-dataverse.example.org
api_token = YOUR_TOKEN
```

Keep the real token only in your local configuration, which is ignored by Git. If `DATAVERSE_API_TOKEN` is set in your environment, it overrides the configuration token. Use `unset DATAVERSE_API_TOKEN` in Bash to use the configuration token instead.

```bash
python dataverse_api.py --apply
```

The uploader verifies each file belongs to the stated DOI's latest version and fetches current metadata before writing. It preserves existing categories, restriction settings, and other returned metadata while changing the requested description or folder label. The script reads updates directly from the CSV; the original JSON files are not modified. API requests use multipart `jsonData`, HTTPS, a timeout, and no redirects. Both JSON success responses and Dataverse's plain-text “File Metadata update has been completed” confirmation are supported. All files are checked before the first write.

Updates are sequential, not transactional. If a request fails, processing stops and reports how many updates were confirmed. Check the draft in Dataverse before retrying, especially after a timeout or an unexpected response. Clear both `new_` cells for files already updated successfully, then preview and apply the remaining changes. Avoid concurrent metadata editing while this tool runs. Review the resulting draft in Dataverse and publish it separately if appropriate.

Both scripts accept `--config path/to/config.ini` and `--help`.

## Examples and troubleshooting

Two fictional datasets are included in `data/json_templates/`, including a wrapped nested export. Generate the CSV and enter a description to try the offline preview. Never apply dummy IDs.

- Missing configuration: copy `config.sample.ini` to `config.ini`.
- No JSON files: check `json_input_dir`.
- Existing CSV: preserve your edits before using `--overwrite`.
- Invalid JSON/CSV: check JSON syntax and save spreadsheets as UTF-8 CSV.
- HTTP errors: check the server URL, token permissions, and installation's API support.

The request implementation follows the [Dataverse Native API documentation](https://guides.dataverse.org/en/latest/api/native-api.html#updating-file-metadata). Validate it against a test Dataverse instance before production use; server versions can differ.

## Repository files

- `json_to_csv.py`: the single converter.
- `dataverse_api.py`: offline preview and API uploader.
- `utils.py`: configuration and file helpers.
- `config.sample.ini`: public configuration template.
- `data/json_templates/`: fictional sample inputs.
- `LICENSE`: MIT license.
