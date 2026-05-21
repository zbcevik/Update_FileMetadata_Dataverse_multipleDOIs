"""
Convert JSON files to CSV format
Generates CSV with DOI, dataset name, and file metadata columns

Supports both Dataverse JSON structures:
  - Modern "search/export" format: top-level keys + latestVersion
  - Legacy "datasetVersion" format from older API endpoints
"""

import os
import sys
import argparse
from typing import List, Dict, Any, Optional
from utils import (
    load_json_file,
    save_csv_file,
    get_json_files_from_directory
)


def _get_version_block(json_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Return whichever version block is present in the JSON.

    Dataverse exports use one of two keys depending on the API endpoint:
      - /api/datasets/export  → "datasetVersion"
      - /api/search or newer  → "latestVersion"
    We check both so the rest of the code only has to deal with one object.
    """
    for key in ("latestVersion", "datasetVersion"):
        block = json_data.get(key)
        if isinstance(block, dict) and block:
            return block
    return None


def extract_doi(json_data: Dict[str, Any]) -> str:
    """
    Extract a DOI from common Dataverse JSON field names.

    Priority order:
      1. Top-level datasetPersistentId
      2. datasetPersistentId inside the version block (latestVersion / datasetVersion)
      3. Top-level persistentUrl  ← this is where your sample file stores it
      4. Top-level identifier
    """
    if json_data.get("datasetPersistentId"):
        return json_data["datasetPersistentId"]

    version_block = _get_version_block(json_data)
    if version_block and version_block.get("datasetPersistentId"):
        return version_block["datasetPersistentId"]

    if json_data.get("persistentUrl"):
        return json_data["persistentUrl"]

    if json_data.get("identifier"):
        return json_data["identifier"]

    return ""


def extract_title_from_citation(json_data: Dict[str, Any]) -> str:
    """
    Extract the dataset title from nested Dataverse citation metadata.

    Looks in (in order):
      1. Top-level datasetName / title shortcuts
      2. metadataBlocks.citation.fields inside latestVersion or datasetVersion
    """
    if json_data.get("datasetName"):
        return json_data["datasetName"]
    if json_data.get("title"):
        return json_data["title"]

    version_block = _get_version_block(json_data)
    if not version_block:
        return "Unknown Dataset"

    fields = (
        version_block
        .get("metadataBlocks", {})
        .get("citation", {})
        .get("fields") or []
    )
    for field in fields:
        if field.get("typeName") == "title":
            value = field.get("value")
            if isinstance(value, str):
                return value
            if isinstance(value, dict):
                return value.get("value", "")
            if isinstance(value, list) and value:
                first = value[0]
                return first.get("value", "") if isinstance(first, dict) else str(first)

    return "Unknown Dataset"


def extract_files(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Return the list of file entries from whichever structure is present.

    Checks (in order):
      1. latestVersion.files  ← your sample file
      2. datasetVersion.files ← older export format
      3. Top-level data[]     ← some legacy formats
      4. Top-level files[]
    """
    version_block = _get_version_block(json_data)
    if version_block:
        files = version_block.get("files")
        if isinstance(files, list):
            return files

    if isinstance(json_data.get("data"), list):
        return json_data["data"]
    if isinstance(json_data.get("files"), list):
        return json_data["files"]

    return []


def get_file_info(file_entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalise a single file entry from the Dataverse JSON.

    Each entry has two layers:
      - Outer (file_entry):  label, description, directoryLabel, restricted, categories
      - Inner (dataFile):    id, filename, filesize, contentType, md5, …

    Description lives on the outer layer and is available even for
    restricted files — no API key required to read it from the JSON.
    """
    data_file = file_entry.get("dataFile")
    if not isinstance(data_file, dict):
        data_file = file_entry   # fallback for flat structures

    # Prefer outer-layer directoryLabel; fall back to inner one
    directory_label = (
        file_entry.get("directoryLabel")
        or data_file.get("directoryLabel", "")
    )

    return {
        "id":           data_file.get("id", ""),
        "label":        file_entry.get("label") or data_file.get("filename", ""),
        "description":  file_entry.get("description", ""),   # outer layer — always present
        "directoryLabel": directory_label,
        "filesize":     data_file.get("filesize", ""),
        "contentType":  data_file.get("contentType", data_file.get("dataType", "")),
        "restricted":   file_entry.get("restricted", False),
        "md5":          data_file.get("md5", ""),
        "categories":   ", ".join(file_entry.get("categories") or []),
    }


def json_to_csv_converter(
    json_files: List[str],
    output_csv: str,
    dataset_names: Dict[str, str] = None,
) -> None:
    """
    Convert multiple Dataverse JSON metadata files into a single CSV.

    Args:
        json_files:    List of paths to JSON files.
        output_csv:    Output CSV file path.
        dataset_names: Optional {DOI: name} override map.
    """
    csv_rows = []
    dataset_names = dataset_names or {}

    for json_file in json_files:
        try:
            print(f"Processing: {json_file}")
            json_data = load_json_file(json_file)

            doi = extract_doi(json_data)
            if not doi:
                print(f"  Warning: No DOI found in {json_file}")
                continue

            dataset_name = dataset_names.get(doi) or extract_title_from_citation(json_data)
            files = extract_files(json_data)

            if not files:
                print(f"  Warning: No files found in {json_file}")
                csv_rows.append({
                    "DOI": doi,
                    "dataset_name": dataset_name,
                    "file_id": "",
                    "file_label": "",
                    "file_description": "",
                    "file_path": "",
                    "file_size": "",
                    "content_type": "",
                    "restricted": "",
                    "md5": "",
                    "categories": "",
                    "original_description": "",
                    "new_description": "",
                    "new_file_path": "",
                    "status": "no_files",
                })
                continue

            for file_entry in files:
                info = get_file_info(file_entry)
                csv_rows.append({
                    "DOI": doi,
                    "dataset_name": dataset_name,
                    "file_id": info["id"],
                    "file_label": info["label"],
                    "file_description": info["description"],
                    "file_path": info["directoryLabel"],
                    "file_size": str(info["filesize"]),
                    "content_type": info["contentType"],
                    "restricted": str(info["restricted"]),
                    "md5": info["md5"],
                    "categories": info["categories"],
                    "original_description": info["description"],
                    "new_description": "",
                    "new_file_path": "",
                    "status": "pending",
                })

        except Exception as e:
            print(f"  Error processing {json_file}: {e}")
            continue

    if csv_rows:
        fieldnames = [
            "DOI",
            "dataset_name",
            "file_id",
            "file_label",
            "file_description",
            "file_path",
            "file_size",
            "content_type",
            "restricted",
            "md5",
            "categories",
            "original_description",
            "new_description",
            "new_file_path",
            "status",
        ]
        save_csv_file(csv_rows, output_csv, fieldnames)
        print(f"\nSuccessfully converted {len(csv_rows)} rows to {output_csv}")
    else:
        print("No data to convert")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Dataverse JSON metadata files to CSV format"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="./data/json_templates",
        help="Directory containing JSON files (default: ./data/json_templates)",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="./data/metadata.csv",
        help="Output CSV file path (default: ./data/metadata.csv)",
    )
    parser.add_argument(
        "--json-file",
        type=str,
        help="Single JSON file to convert (alternative to --input-dir)",
    )

    args = parser.parse_args()

    json_files = [args.json_file] if args.json_file else get_json_files_from_directory(args.input_dir)

    if not json_files:
        print(f"No JSON files found in {args.input_dir}")
        sys.exit(1)

    json_to_csv_converter(json_files, args.output_csv)


if __name__ == "__main__":
    main()
