"""
Utility functions for handling JSON, CSV, and Dataverse API interactions
"""

import json
import csv
import os
from typing import List, Dict, Any
from datetime import datetime


def load_json_file(filepath: str) -> Dict[str, Any]:
    """
    Load a JSON file and return its contents
    
    Args:
        filepath: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(data: Dict[str, Any], filepath: str, indent: int = 2) -> None:
    """
    Save data to a JSON file
    
    Args:
        data: Dictionary to save
        filepath: Path where to save the JSON file
        indent: JSON indentation level
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)


def load_csv_file(filepath: str) -> List[Dict[str, str]]:
    """
    Load a CSV file and return as list of dictionaries
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        List of dictionaries where each row is a dictionary
    """
    rows = []
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def save_csv_file(data: List[Dict[str, str]], filepath: str, fieldnames: List[str]) -> None:
    """
    Save list of dictionaries to a CSV file
    
    Args:
        data: List of dictionaries to save
        filepath: Path where to save the CSV file
        fieldnames: List of column names in the CSV
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def extract_metadata_from_json(json_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract file metadata from JSON structure
    
    Expected JSON structure:
    {
        "datasetPersistentId": "doi:...",
        "dataset": { "version": "..." },
        "data": [ {"label": "...", "directoryLabel": "...", ...}, ... ]
    }
    
    Args:
        json_data: The JSON data structure
        
    Returns:
        Dictionary with extracted metadata
    """
    metadata = {}
    
    # Extract DOI
    if "datasetPersistentId" in json_data:
        metadata["DOI"] = json_data["datasetPersistentId"]
    
    # Extract dataset version
    if "dataset" in json_data and "version" in json_data["dataset"]:
        metadata["dataset_version"] = json_data["dataset"]["version"]
    
    # Extract file information
    if "data" in json_data and isinstance(json_data["data"], list):
        metadata["file_count"] = len(json_data["data"])
        # Get first file details as example
        if json_data["data"]:
            first_file = json_data["data"][0]
            metadata["first_file_label"] = first_file.get("label", "")
            metadata["first_file_directory"] = first_file.get("directoryLabel", "")
    
    return metadata


def create_dataverse_json_structure(doi: str, dataset_name: str, files_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create a Dataverse-compatible JSON structure for files
    
    Args:
        doi: Dataset DOI
        dataset_name: Name of the dataset
        files_metadata: List of file metadata dictionaries
        
    Returns:
        Dictionary with Dataverse-compatible structure
    """
    return {
        "datasetPersistentId": doi,
        "datasetName": dataset_name,
        "dataset": {
            "version": 1,
            "releaseTime": datetime.now().isoformat()
        },
        "data": files_metadata,
        "lastUpdated": datetime.now().isoformat()
    }


def validate_csv_row(row: Dict[str, str], required_fields: List[str]) -> tuple[bool, str]:
    """
    Validate a CSV row has all required fields
    
    Args:
        row: Dictionary representing a CSV row
        required_fields: List of required field names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in row or not row[field].strip()]
    if missing_fields:
        return False, f"Missing fields: {', '.join(missing_fields)}"
    return True, ""


def get_json_files_from_directory(directory: str) -> List[str]:
    """
    Get all JSON files from a directory
    
    Args:
        directory: Path to directory containing JSON files
        
    Returns:
        List of absolute paths to JSON files
    """
    json_files = []
    if os.path.isdir(directory):
        for filename in os.listdir(directory):
            if filename.endswith('.json'):
                json_files.append(os.path.join(directory, filename))
    return sorted(json_files)
