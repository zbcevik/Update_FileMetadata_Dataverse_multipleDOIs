"""Combine Dataverse dataset JSON files into one editable CSV."""
import argparse
from pathlib import Path
from utils import load_config, load_json_file, save_csv_file

COLUMNS = ["DOI", "dataset_name", "file_id", "file_label", "original_description",
           "file_path", "file_size", "content_type", "restricted", "categories",
           "new_description", "new_file_path"]


def normalize_doi(value):
    value = str(value).strip()
    for prefix in ("https://doi.org/", "http://doi.org/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
    return value if value.startswith("doi:") else "doi:" + value


def dataset_rows(payload):
    if isinstance(payload.get("data"), dict):
        payload = payload["data"]
    version = payload.get("latestVersion") or payload.get("datasetVersion") or {}
    doi = payload.get("datasetPersistentId") or version.get("datasetPersistentId") or payload.get("persistentUrl")
    if not doi and payload.get("authority") and payload.get("identifier"):
        doi = f"{payload['authority']}/{payload['identifier']}"
    if not doi:
        raise ValueError("Dataset has no complete DOI")
    doi = normalize_doi(doi)
    if not doi.startswith("doi:10.") or "/" not in doi:
        raise ValueError("Dataset DOI must contain an authority and identifier")
    title = payload.get("datasetName") or payload.get("title")
    if not title:
        fields = version.get("metadataBlocks", {}).get("citation", {}).get("fields", [])
        title = next((f.get("value") for f in fields if f.get("typeName") == "title"), "Unknown Dataset")
    entries = version.get("files")
    if entries is None:
        entries = payload.get("files", payload.get("data", []))
    if not isinstance(entries, list):
        raise ValueError("Dataset files must be a list")
    rows = []
    for entry in entries:
        data_file = entry.get("dataFile", entry)
        file_id = str(data_file.get("id", ""))
        if not file_id.isascii() or not file_id.isdigit() or int(file_id) < 1:
            raise ValueError("Every file must have a positive numeric file ID")
        rows.append(dict(zip(COLUMNS, [doi, title, file_id,
            entry.get("label") or data_file.get("filename", ""),
            entry.get("description", ""), entry.get("directoryLabel", ""),
            data_file.get("filesize", ""), data_file.get("contentType", data_file.get("dataType", "")),
            entry.get("restricted", False), ", ".join(entry.get("categories") or []), "", ""])))
    return rows


def convert(input_dir, output_csv, overwrite=False):
    paths = sorted(p for p in Path(input_dir).glob("*") if p.is_file() and p.suffix.lower() == ".json")
    if not paths:
        raise ValueError("No JSON files found in input directory")
    if Path(output_csv).exists() and not overwrite:
        raise ValueError("Output CSV already exists; use --overwrite only after saving your edits elsewhere")
    rows = []
    seen = set()
    for path in paths:
        try:
            extracted = dataset_rows(load_json_file(path))
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError(f"{path.name}: {error}") from error
        for row in extracted:
            if row["file_id"] in seen:
                raise ValueError(f"Duplicate file ID: {row['file_id']}")
            seen.add(row["file_id"])
        rows.extend(extracted)
    save_csv_file(rows, output_csv, COLUMNS)
    print(f"Created {output_csv}: {len(rows)} files from {len(paths)} datasets")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.ini")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing CSV")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        convert(config["paths"]["json_input_dir"], config["paths"]["csv_file"], args.overwrite)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
