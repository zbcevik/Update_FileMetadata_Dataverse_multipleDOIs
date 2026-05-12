"""
Dataverse API interface for bulk updating file metadata
Handles authentication and communication with Dataverse instances
"""

import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List, Tuple
from utils import load_json_file, load_csv_file


class DataverseAPI:
    """Interface for Dataverse API operations"""
    
    def __init__(self, server_url: str, api_token: str):
        """
        Initialize Dataverse API client
        
        Args:
            server_url: URL of Dataverse instance (e.g., https://dataverse.example.org)
            api_token: API token for authentication
        """
        self.server_url = server_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            "X-Dataverse-key": api_token,
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, json_data: Dict = None) -> Tuple[bool, Any]:
        """
        Make HTTP request to Dataverse API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Form data for request
            json_data: JSON data for request
            
        Returns:
            Tuple of (success, response_data)
        """
        url = f"{self.server_url}/api/v1{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, data=data, json=json_data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, data=data, json=json_data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers)
            else:
                return False, f"Unsupported method: {method}"
            
            if response.status_code in [200, 201, 204]:
                return True, response.json() if response.text else {}
            else:
                return False, f"Status {response.status_code}: {response.text}"
        
        except Exception as e:
            return False, str(e)
    
    def get_dataset_metadata(self, dataset_id: str) -> Tuple[bool, Dict]:
        """
        Get metadata for a dataset
        
        Args:
            dataset_id: Dataset PID or ID
            
        Returns:
            Tuple of (success, metadata)
        """
        return self._make_request("GET", f"/datasets/{dataset_id}")
    
    def get_file_metadata(self, file_id: str) -> Tuple[bool, Dict]:
        """
        Get metadata for a specific file
        
        Args:
            file_id: File ID
            
        Returns:
            Tuple of (success, file_metadata)
        """
        return self._make_request("GET", f"/files/{file_id}")
    
    def update_file_metadata(self, file_id: str, metadata: Dict) -> Tuple[bool, Any]:
        """
        Update metadata for a specific file
        
        Args:
            file_id: File ID
            metadata: Dictionary with metadata to update (e.g., {"description": "new description", "directoryLabel": "path"})
            
        Returns:
            Tuple of (success, response)
        """
        return self._make_request("POST", f"/files/{file_id}", data=metadata)
    
    def get_dataset_files(self, dataset_id: str) -> Tuple[bool, List[Dict]]:
        """
        Get list of files in a dataset
        
        Args:
            dataset_id: Dataset PID or ID
            
        Returns:
            Tuple of (success, list of files)
        """
        success, data = self._make_request("GET", f"/datasets/{dataset_id}/versions/latest/files")
        if success and "data" in data:
            return True, data["data"]
        return success, data
    
    def test_connection(self) -> bool:
        """
        Test connection to Dataverse server
        
        Returns:
            True if connection successful
        """
        success, _ = self._make_request("GET", "/info/version")
        return success


def push_updates_from_csv(csv_file: str, server_url: str, api_token: str, dry_run: bool = True) -> None:
    """
    Push metadata updates from CSV file to Dataverse
    
    Args:
        csv_file: Path to CSV file with updates
        server_url: Dataverse server URL
        api_token: API token for authentication
        dry_run: If True, show what would be updated without making changes
    """
    # Initialize API
    api = DataverseAPI(server_url, api_token)
    
    # Test connection
    print("Testing connection to Dataverse...")
    if not api.test_connection():
        print("✗ Failed to connect to Dataverse server")
        sys.exit(1)
    print("✓ Connected to Dataverse")
    
    # Load CSV
    try:
        rows = load_csv_file(csv_file)
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        sys.exit(1)
    
    # Group by DOI and file ID
    updates: Dict[str, List[Dict]] = {}
    for row in rows:
        doi = row.get("DOI", "").strip()
        file_id = row.get("file_id", "").strip()
        
        if not doi or not file_id:
            continue
        
        if doi not in updates:
            updates[doi] = []
        
        # Determine what changed
        new_desc = row.get("new_description", "").strip()
        new_path = row.get("new_file_path", "").strip()
        
        if new_desc or new_path:
            updates[doi].append({
                "file_id": file_id,
                "file_label": row.get("file_label", ""),
                "original_description": row.get("original_description", ""),
                "new_description": new_desc,
                "new_file_path": new_path
            })
    
    # Process updates
    total_updates = 0
    successful_updates = 0
    
    for doi, file_updates in updates.items():
        print(f"\n{'='*60}")
        print(f"Dataset: {doi}")
        print(f"Files to update: {len(file_updates)}")
        
        for update in file_updates:
            print(f"\n  File ID: {update['file_id']}")
            print(f"  Label: {update['file_label']}")
            
            metadata = {}
            if update['new_description']:
                print(f"    Description: {update['original_description'][:50]}... → {update['new_description'][:50]}...")
                metadata['description'] = update['new_description']
            
            if update['new_file_path']:
                print(f"    Path: → {update['new_file_path']}")
                metadata['directoryLabel'] = update['new_file_path']
            
            if not dry_run and metadata:
                success, response = api.update_file_metadata(update['file_id'], metadata)
                if success:
                    print("    ✓ Updated")
                    successful_updates += 1
                else:
                    print(f"    ✗ Error: {response}")
            
            total_updates += 1
    
    # Summary
    print(f"\n{'='*60}")
    if dry_run:
        print(f"DRY RUN: Would update {total_updates} files")
        print("Use --no-dry-run to apply changes")
    else:
        print(f"Updated {successful_updates}/{total_updates} files successfully")


def main():
    parser = argparse.ArgumentParser(
        description="Push metadata updates to Dataverse"
    )
    parser.add_argument(
        "--csv-file",
        type=str,
        required=True,
        help="CSV file with metadata updates"
    )
    parser.add_argument(
        "--server-url",
        type=str,
        default=os.getenv("DATAVERSE_SERVER_URL", ""),
        help="Dataverse server URL (or set DATAVERSE_SERVER_URL env var)"
    )
    parser.add_argument(
        "--api-token",
        type=str,
        default=os.getenv("DATAVERSE_API_TOKEN", ""),
        help="Dataverse API token (or set DATAVERSE_API_TOKEN env var)"
    )
    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Apply changes (by default, only shows what would be updated)"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.server_url:
        print("Error: Dataverse server URL required (--server-url or DATAVERSE_SERVER_URL env var)")
        sys.exit(1)
    
    if not args.api_token:
        print("Error: Dataverse API token required (--api-token or DATAVERSE_API_TOKEN env var)")
        sys.exit(1)
    
    if not os.path.exists(args.csv_file):
        print(f"Error: CSV file not found: {args.csv_file}")
        sys.exit(1)
    
    push_updates_from_csv(args.csv_file, args.server_url, args.api_token, dry_run=not args.no_dry_run)


if __name__ == "__main__":
    main()
