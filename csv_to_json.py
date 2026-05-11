"""
Convert CSV file back to JSON files for Dataverse update
Allows users to update metadata via CSV and convert back to JSON format
"""

import os
import sys
import argparse
from typing import Dict, List, Any
from utils import load_csv_file, save_json_file


def csv_to_json_converter(csv_file: str, output_dir: str = "./data/json_output") -> None:
    """
    Convert CSV file to JSON files grouped by DOI
    
    Args:
        csv_file: Path to the CSV file
        output_dir: Directory where JSON files will be saved
    """
    try:
        csv_rows = load_csv_file(csv_file)
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        sys.exit(1)
    
    # Group rows by DOI
    datasets: Dict[str, Dict[str, Any]] = {}
    
    for row in csv_rows:
        doi = row.get("DOI", "").strip()
        if not doi:
            print("Warning: Skipping row with empty DOI")
            continue
        
        # Initialize dataset structure if not exists
        if doi not in datasets:
            datasets[doi] = {
                "datasetPersistentId": doi,
                "datasetName": row.get("dataset_name", ""),
                "dataset": {
                    "version": 1,
                    "releaseTime": ""
                },
                "data": []
            }
        
        # Extract file information from CSV
        file_id = row.get("file_id", "").strip()
        if file_id:  # Only add file if file_id exists
            file_entry = {
                "id": file_id,
                "label": row.get("file_label", ""),
                "description": row.get("new_description", "") or row.get("original_description", ""),
                "directoryLabel": row.get("new_file_path", "") or row.get("file_path", ""),
                "filesize": int(row.get("file_size", "0")) if row.get("file_size", "").isdigit() else 0,
                "dataType": row.get("file_type", ""),
                "status": row.get("status", "updated")
            }
            datasets[doi]["data"].append(file_entry)
    
    # Save JSON files
    os.makedirs(output_dir, exist_ok=True)
    saved_count = 0
    
    for doi, dataset_data in datasets.items():
        # Create filename from DOI (replace forward slashes and colons)
        safe_doi = doi.replace("/", "_").replace(":", "")
        output_file = os.path.join(output_dir, f"{safe_doi}.json")
        
        try:
            save_json_file(dataset_data, output_file)
            print(f"✓ Created: {output_file}")
            saved_count += 1
        except Exception as e:
            print(f"✗ Error saving {output_file}: {str(e)}")
    
    print(f"\nSuccessfully converted {saved_count} JSON files to {output_dir}")
    print("\nNext step: Use these JSON files with the Dataverse API to update your datasets")


def main():
    parser = argparse.ArgumentParser(
        description="Convert CSV metadata to JSON format for Dataverse"
    )
    parser.add_argument(
        "--csv-file",
        type=str,
        required=True,
        help="Input CSV file with updated metadata"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./data/json_output",
        help="Output directory for JSON files (default: ./data/json_output)"
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)
    
    csv_to_json_converter(args.csv_file, args.output_dir)


if __name__ == "__main__":
    main()
