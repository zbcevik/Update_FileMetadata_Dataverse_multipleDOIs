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
            doi = json_data.get("datasetPersistentId", "")
            if not doi:
                print(f"  Warning: No DOI found in {json_file}")
                continue
            
            # Get dataset name
            dataset_name = (dataset_names.get(doi) or 
                           json_data.get("datasetName", "Unknown Dataset"))
            
            # Extract file information
            files = json_data.get("data", [])
            
            for file_info in files:
                row = {
                    "DOI": doi,
                    "dataset_name": dataset_name,
                    "file_id": file_info.get("id", ""),
                    "file_label": file_info.get("label", ""),
                    "file_description": file_info.get("description", ""),
                    "file_path": file_info.get("directoryLabel", ""),
                    "file_size": str(file_info.get("filesize", "")),
                    "file_type": file_info.get("dataType", ""),
                    "original_description": file_info.get("description", ""),
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
                    "file_type": "",
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
            "file_type",
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
