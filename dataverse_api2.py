"""
Bulk update Dataverse file metadata from a folder of JSON files.

Each JSON file must look like:

{
  "datasetPersistentId": "doi:10.80240/FK2/6RZD0P",
  "data": [
    {
      "id": "70236",
      "label": "file_metadata.json",
      "description": "New description",
      "directoryLabel": "Data/Json"
    }
  ]
}
"""

import os
import sys
import json
import argparse
import requests


def test_connection(server_url: str, api_token: str) -> bool:
    """Test Dataverse API connection"""
    url = f"{server_url.rstrip('/')}/api/info/version"
    headers = {"X-Dataverse-key": api_token}

    try:
        r = requests.get(url, headers=headers)
        return r.status_code == 200
    except Exception:
        return False


def update_file_metadata(server_url: str, api_token: str, file_id: str, metadata: dict):
    """
    Update file metadata using Dataverse-required multipart/form-data.
    THIS is what fixes the 415 error.
    """
    url = f"{server_url.rstrip('/')}/api/files/{file_id}/metadata"
    headers = {
        "X-Dataverse-key": api_token
    }

    files = {
        "jsonData": (None, json.dumps(metadata), "application/json")
    }

    response = requests.post(url, headers=headers, files=files)
    return response


def push_json_folder(
    folder_path: str,
    server_url: str,
    api_token: str,
    dry_run: bool = True,
):
    """Push all JSON files in a folder to Dataverse"""

    if not test_connection(server_url, api_token):
        print("✗ Cannot connect to Dataverse")
        sys.exit(1)

    json_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(".json")
    ]

    if not json_files:
        print("No JSON files found.")
        return

    print(f"✓ Found {len(json_files)} JSON files")

    for json_name in json_files:
        json_path = os.path.join(folder_path, json_name)
        print(f"\nProcessing: {json_name}")

        with open(json_path, "r", encoding="utf-8") as f:
            payload = json.load(f)

        files = payload.get("data", [])
        print(f" Files in JSON: {len(files)}")

        for entry in files:
            file_id = entry.get("id")
            if not file_id:
                print("  ⚠ Skipping entry without file ID")
                continue

            metadata = {}

            if entry.get("description"):
                metadata["description"] = entry["description"]

            if entry.get("directoryLabel"):
                metadata["directoryLabel"] = entry["directoryLabel"]

            # IMPORTANT: prevents category wipe
            metadata["categories"] = ["Data"]

            if not metadata:
                print(f"  Skipping file {file_id} (no updates)")
                continue

            print(f"  File {file_id}: {metadata}")

            if not dry_run:
                r = update_file_metadata(server_url, api_token, file_id, metadata)

                if r.status_code == 200:
                    print("   ✓ Updated")
                else:
                    print(f"   ✗ Failed {r.status_code}: {r.text}")


def main():
    parser = argparse.ArgumentParser(
        description="Push Dataverse file metadata from JSON folder"
    )

    parser.add_argument(
        "--json-folder",
        required=True,
        help="Folder containing JSON metadata files",
    )

    parser.add_argument(
        "--server-url",
        required=True,
        help="Dataverse server URL (e.g. https://demo.borealisdata.ca)",
    )

    parser.add_argument(
        "--api-token",
        required=True,
        help="Dataverse API token",
    )

    parser.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Actually apply changes",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.json_folder):
        print(f"Folder not found: {args.json_folder}")
        sys.exit(1)

    push_json_folder(
        args.json_folder,
        args.server_url,
        args.api_token,
        dry_run=not args.no_dry_run,
    )


if __name__ == "__main__":
    main()
