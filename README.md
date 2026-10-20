# Borealis/Dataverse Bulk File Metadata Updater

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776AB.svg)](https://www.python.org/)

A Python tool for reviewing and updating file descriptions and folder labels across multiple datasets using one spreadsheet.

Export dataset metadata as JSON, combine the exports into one CSV, edit the proposed values, preview the changes offline, and apply the reviewed updates to Borealis/Dataverse.

**Dataset JSON files → CSV → edit → preview → apply**

The tool updates file metadata. It does not upload or replace file contents, download dataset exports, or publish datasets.

> [!CAUTION]
> Review the CSV and run the offline preview before using `--apply`.
> Test with one dataset on https://demo.borealisdata.ca first.
> Apply mode sends updates without an additional confirmation prompt.
> Updates are sequential and cannot be rolled back automatically.

## Supported environment

- Python 3.9 or later.
- The dependencies listed in `requirements.txt`.
- Dataset JSON exports containing complete DOIs and positive numeric file IDs.
- A Dataverse API token with permission to edit the target datasets.
- An HTTPS Dataverse server supporting the file-metadata update API.

Dataverse versions and local configurations can differ. Validate the workflow against your institution's test or demo server before production use.

## Install and configure

Clone the repository and open its root folder:

```bash
git clone --branch config_update https://github.com/zbcevik/Update_FileMetadata_Dataverse_multipleDOIs.git
cd Update_FileMetadata_Dataverse_multipleDOIs
```

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate with `.venv\Scripts\activate` and copy the configuration using your file manager.

## Configuration and API-token setup

The repository includes `config.sample.ini` as a configuration template. Copy it to `config.ini`, then enter your settings and API token in that local copy. Your private `config.ini` should not be uploaded to GitHub.

```bash
cp config.sample.ini config.ini
```

On macOS/Linux, restrict access to the local file:

```bash
chmod 600 config.ini
```

Edit the settings:

```ini
[dataverse]
server_url = https://demo.borealisdata.ca
api_token = YOUR API TOKEN

[paths]
json_input_dir = ../dataverse_metadata_inputs
csv_file = ./data/metadata.csv
```

A nonempty `DATAVERSE_API_TOKEN` environment variable overrides the token in `config.ini`. In Bash, run `unset DATAVERSE_API_TOKEN` to use the configuration token instead.

Create the input directory and place your real dataset JSON exports there. The example path keeps those exports outside this repository.

Relative paths are resolved from the directory containing the configuration file.The CSV's parent directory is created automatically.

Before applying updates, enter your token in local `config.ini` or set `DATAVERSE_API_TOKEN`.

`config.ini` is ignored by Git. Never commit or share a configured copy. Both scripts support `--config path/to/config.ini`.

## 1. Create the spreadsheet

Obtain one dataset JSON export per DOI from the target Dataverse server. This tool does not download exports.

Place the exports directly inside the configured `json_input_dir`. The converter reads JSON files in that directory; it does not search subdirectories.

Use exports from the same server that you intend to update. File IDs identify files on that server.

Keep an unchanged copy of the original exports before preparing updates.

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
| new_description | Replace with a new description |
| new_file_path | Replace with a new folder label |

Edit only the two `new_` columns. Blank or whitespace-only cells mean **leave unchanged**; clearing a field is not supported. There is no status column. Remove rows or leave the new columns blank to exclude files. A nonblank value is an update request even if it matches the original.

## 3. Preview the proposed changes

```bash
python dataverse_api.py
```

Preview displays the requested description and folder-label changes. It sends no network requests and does not require an API token.

Check the DOI, file ID, requested fields, and total file count. The preview should include only files you intended to update.

Offline preview does not check server connectivity, token permissions, whether the files belong to the datasets, or whether the server will accept the changes. Those checks occur during apply mode.

## 4. Apply the reviewed changes

To apply, enter a token with permission to edit the datasets in your local `config.ini`:

```ini
[dataverse]
server_url = https://your-dataverse.example.org
api_token = YOUR_TOKEN
```

Keep the token in ignored local `config.ini` or the `DATAVERSE_API_TOKEN` environment variable. Never commit or share it.

```bash
python dataverse_api.py --apply
```

The uploader verifies each file belongs to the stated DOI's latest version and fetches current metadata before writing. It preserves existing categories, restriction settings, and other returned metadata while changing the requested description or folder label. The script reads updates directly from the CSV; the original JSON files are not modified. API requests use multipart `jsonData`, HTTPS, a timeout, and no redirects. Both JSON success responses and Dataverse's plain-text “File Metadata update has been completed” confirmation are supported. All files are checked before the first write.

## 5. Verify the results

Open each affected dataset in Dataverse and inspect its latest draft.

- Confirm that the intended file descriptions changed.
- Confirm that the intended folder labels changed.
- Check that file names, categories, restrictions, and other metadata remain as expected.
- Confirm that all requested files were processed.

The tool does not publish datasets. Review and publish the draft separately if appropriate.

## Errors and recovery

Updates are sequential, not transactional. A later failure does not undo earlier successful updates.

If an update fails, the script stops and reports the file ID and the number of confirmed updates. Inspect the dataset in Dataverse before retrying. A timeout or unexpected response can occur after the server has already accepted an update.

Clear both `new_` columns for files whose changes are already confirmed. Preview the remaining requests before applying them again.

To correct an incorrect value already applied to the server, enter the desired value in the corresponding new column, preview it, and apply a corrective update.

Restoring a local CSV or JSON backup does not restore server metadata. The tool has no automatic rollback. If correction requires clearing a field, use the Dataverse interface or another supported method, because blank CSV update cells mean leave unchanged.

Both scripts accept `--config path/to/config.ini` and `--help`.

## Examples and troubleshooting

Two fictional datasets are included in `data/json_templates/`, including a wrapped nested export. Generate the CSV and enter a description to try the offline preview. Never apply dummy IDs.

- Missing configuration: copy `config.sample.ini` to `config.ini`.
- No JSON files: check `json_input_dir`.
- Existing CSV: preserve your edits before using `--overwrite`.
- Invalid JSON/CSV: check JSON syntax and save spreadsheets as UTF-8 CSV.
- HTTP errors: check the server URL, token permissions, and installation's API support.

The request implementation follows the [Dataverse Native API documentation](https://guides.dataverse.org/en/latest/api/native-api.html#updating-file-metadata). Validate it against a test Dataverse instance before production use; server versions can differ.

## Security

- Keep API tokens in ignored local configuration or the `DATAVERSE_API_TOKEN` environment variable.
- Never include tokens or private metadata in public issues, screenshots, logs, or commits.
- If a token is exposed, revoke it and create a replacement.
- Use HTTPS for the target server.
- Review `git status` and staged changes before committing.
- Keep real dataset exports and generated CSV files private unless you have confirmed that they are suitable for publication.

## Repository files

- `json_to_csv.py`: combines dataset JSON exports into one editable CSV.
- `dataverse_api.py`: previews CSV requests offline or applies them to Dataverse.
- `utils.py`: shared configuration and file-reading helpers.
- `requirements.txt`: Python dependencies.
- `config.sample.ini`: public configuration template.
- `.gitignore`: excludes local configuration and selected generated files.
- `data/json_templates/`: fictional examples for testing conversion and preview.
- `LICENSE`: MIT license.
