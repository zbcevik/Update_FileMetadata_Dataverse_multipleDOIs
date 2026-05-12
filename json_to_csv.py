"""
Convert JSON files to CSV format
Generates CSV with DOI, dataset name, and file metadata columns
"""

import os
import sys
import argparse
from typing import List, Dict, Any
from utils import (
    load_json_file,
    save_csv_file,
    get_json_files_from_directory
)


def extract_doi(json_data: Dict[str, Any]) -> str:
    """Extract a DOI from common Dataverse JSON field names."""
    if "datasetPersistentId" in json_data and json_data["datasetPersistentId"]:
        return json_data["datasetPersistentId"]
    if "datasetVersion" in json_data and isinstance(json_data["datasetVersion"], dict):
        doi = json_data["datasetVersion"].get("datasetPersistentId", "")
        if doi:
            return doi
    if "persistentUrl" in json_data and json_data["persistentUrl"]:
        return json_data["persistentUrl"]
    if "identifier" in json_data and json_data["identifier"]:
        return json_data["identifier"]
    return ""


def extract_title_from_citation(json_data: Dict[str, Any]) -> str:
    """Extract dataset title from nested citation metadata."""
    if "datasetName" in json_data and json_data["datasetName"]:
        return json_data["datasetName"]

    if "title" in json_data and json_data["title"]:
        return json_data["title"]

    dataset_version = json_data.get("datasetVersion")
    if isinstance(dataset_version, dict):
        citation = dataset_version.get("metadataBlocks", {}).get("citation", {})
        fields = citation.get("fields") or []
        for field in fields:
            if field.get("typeName") == "title":
                value = field.get("value")
                if isinstance(value, str):
                    return value
                if isinstance(value, dict):
                    return value.get("value", "")
                if isinstance(value, list) and value:
                    first = value[0]
                    if isinstance(first, dict):
                        return first.get("value", "")
                    return str(first)
    return "Unknown Dataset"


def extract_files(json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return file entries from either modern Dataverse or legacy JSON formats."""
    # Check datasetVersion.files first (nested structure from Dataverse API)
    if "datasetVersion" in json_data and isinstance(json_data["datasetVersion"], dict):
        dataset_version = json_data["datasetVersion"]
        if "files" in dataset_version and isinstance(dataset_version["files"], list):
            return dataset_version["files"]
    
    # Check top-level data/files
    if "data" in json_data and isinstance(json_data["data"], list):
        return json_data["data"]
    if "files" in json_data and isinstance(json_data["files"], list):
        return json_data["files"]
    return []


def get_file_info(file_info: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize file metadata from both `data` and `files` JSON structures."""
    data_file = file_info.get("dataFile") if isinstance(file_info.get("dataFile"), dict) else file_info
    return {
        "id": data_file.get("id", ""),
        "label": file_info.get("label", "") or data_file.get("filename", ""),
        "description": file_info.get("description", ""),
        "directoryLabel": file_info.get("directoryLabel", ""),
        "filesize": data_file.get("filesize", ""),
        "dataType": data_file.get("dataType", data_file.get("contentType", ""))
    }


def json_to_csv_converter(json_files: List[str], output_csv: str, dataset_names: Dict[str, str] = None) -> None:
    """
    Convert multiple JSON files to a single CSV file
    
    Args:
        json_files: List of paths to JSON files
        output_csv: Output CSV file path
        dataset_names: Optional dictionary mapping DOI to dataset name
    """
    csv_rows = []
    dataset_names = dataset_names or {}
    
    for json_file in json_files:
        try:
            print(f"Processing: {json_file}")
            json_data = load_json_file(json_file)
            
            # Extract DOI
            doi = extract_doi(json_data)
            if not doi:
                print(f"  Warning: No DOI found in {json_file}")
                continue
            
            # Get dataset name
            dataset_name = dataset_names.get(doi) or extract_title_from_citation(json_data)
            
            # Extract file information
            files = extract_files(json_data)
            
            for file_info in files:
                normalized = get_file_info(file_info)
                row = {
                    "DOI": doi,
                    "dataset_name": dataset_name,
                    "file_id": normalized.get("id", ""),
                    "file_label": normalized.get("label", ""),
                    "file_description": normalized.get("description", ""),
                    "file_path": normalized.get("directoryLabel", ""),
                    "file_size": str(normalized.get("filesize", "")),
                    "original_description": normalized.get("description", ""),
                    "new_description": "",
                    "new_file_path": "",
                    "status": "pending"
                }
                csv_rows.append(row)
            
            # If no files, still create a row for dataset metadata
            if not files:
                row = {
                    "DOI": doi,
                    "dataset_name": dataset_name,
                    "file_id": "",
                    "file_label": "",
                    "file_description": "",
                    "file_path": "",
                    "file_size": "",
                    "original_description": "",
                    "new_description": "",
                    "new_file_path": "",
                    "status": "no_files"
                }
                csv_rows.append(row)
        
        except Exception as e:
            print(f"  Error processing {json_file}: {str(e)}")
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
            "original_description",
            "new_description",
            "new_file_path",
            "status"
        ]
        save_csv_file(csv_rows, output_csv, fieldnames)
        print(f"\nSuccessfully converted {len(csv_rows)} rows to {output_csv}")
    else:
        print("No data to convert")


def main():
    parser = argparse.ArgumentParser(
        description="Convert JSON metadata files to CSV format"
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default="./data/json_templates",
        help="Directory containing JSON files (default: ./data/json_templates)"
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default="./data/metadata.csv",
        help="Output CSV file path (default: ./data/metadata.csv)"
    )
    parser.add_argument(
        "--json-file",
        type=str,
        help="Single JSON file to convert (alternative to --input-dir)"
    )
    
    args = parser.parse_args()
    
    # Determine which files to process
    if args.json_file:
        json_files = [args.json_file]
    else:
        json_files = get_json_files_from_directory(args.input_dir)
    
    if not json_files:
        print(f"No JSON files found in {args.input_dir}")
        sys.exit(1)
    
    json_to_csv_converter(json_files, args.output_csv)


if __name__ == "__main__":
    main()
