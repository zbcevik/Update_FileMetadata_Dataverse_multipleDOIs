"""Preview or apply CSV file metadata changes to Dataverse."""
import argparse
import copy
import json
import os
from urllib.parse import urlparse
import requests
from utils import load_config, load_csv_file
from json_to_csv import normalize_doi


def planned_updates(rows):
    updates = []
    seen = set()
    for number, row in enumerate(rows, 2):
        changes = {}
        for column, field in (("new_description", "description"), ("new_file_path", "directoryLabel")):
            value = row[column]
            if value.strip():
                changes[field] = value
        if not changes:
            continue
        file_id = row["file_id"].strip()
        doi = normalize_doi(row["DOI"])
        if not file_id.isascii() or not file_id.isdigit() or int(file_id) < 1 or not doi.startswith("doi:10.") or "/" not in doi:
            raise ValueError(f"CSV row {number}: a complete DOI and positive numeric file ID are required")
        if file_id in seen:
            raise ValueError(f"CSV row {number}: duplicate file ID {file_id}")
        seen.add(file_id)
        updates.append((doi, file_id, changes))
    return updates


class DataverseAPI:
    def __init__(self, server_url, api_token):
        parsed = urlparse(server_url)
        if parsed.scheme != "https" or not parsed.netloc or parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("server_url must be an HTTPS URL without credentials, query, or fragment")
        self.base = server_url.rstrip("/") + "/api"
        self.session = requests.Session()
        self.session.headers.update({"X-Dataverse-key": api_token, "Accept": "application/json"})

    def request(self, method, endpoint, **kwargs):
        response = self.session.request(method, self.base + endpoint, timeout=30, allow_redirects=False, **kwargs)
        if response.status_code not in (200, 201):
            detail = response.text.replace(self.session.headers["X-Dataverse-key"], "[REDACTED]")[:2000]
            raise ValueError(f"Dataverse returned HTTP {response.status_code}: {detail}")
        try:
            payload = response.json()
        except ValueError as error:
            # Some Dataverse versions return plain text for successful updates.
            prefix = "File Metadata update has been completed: "
            if (method == "POST" and endpoint.endswith("/metadata")
                    and response.status_code == 200 and response.text.startswith(prefix)):
                try:
                    updated = json.loads(response.text[len(prefix):])
                except ValueError:
                    updated = None
                if isinstance(updated, dict):
                    return updated
            detail = response.text.replace(self.session.headers["X-Dataverse-key"], "[REDACTED]")[:500]
            content_type = response.headers.get("Content-Type", "unspecified")
            raise ValueError(
                f"Dataverse returned HTTP {response.status_code} with a non-JSON response "
                f"(Content-Type: {content_type}; body: {detail or '[empty]'}). "
                "The update may have succeeded"
            ) from error
        if payload.get("status") != "OK":
            raise ValueError("Dataverse reported an unsuccessful operation")
        return payload.get("data")

    def prepare(self, doi, file_id, changes):
        # Verify membership and use latest (including draft) metadata.
        dataset = self.request("GET", "/datasets/:persistentId/versions/:latest", params={"persistentId": doi})
        entries = dataset.get("files", [])
        current = next((entry for entry in entries if str(entry.get("dataFile", {}).get("id")) == file_id), None)
        if current is None:
            raise ValueError(f"File {file_id} does not belong to the latest version of {doi}")
        metadata = copy.deepcopy(current)
        # Translate response field names into writable metadata fields.
        metadata.pop("dataFile", None)
        for key in ("version", "datasetVersionId", "id"):
            metadata.pop(key, None)
        if "restricted" in metadata:
            metadata["restrict"] = metadata.pop("restricted")
        if "tabularTags" in metadata:
            metadata["dataFileTags"] = metadata.pop("tabularTags")
        metadata.update(changes)
        return metadata

    def update(self, file_id, metadata):
        self.request("POST", f"/files/{file_id}/metadata", files={
            "jsonData": (None, json.dumps(metadata), "application/json")})


def run(csv_file, server_url="", api_token="", apply=False):
    updates = planned_updates(load_csv_file(csv_file))
    for doi, file_id, changes in updates:
        print(f"{doi} / file {file_id}: {json.dumps(changes, ensure_ascii=False)}")
    if not apply:
        print(f"Preview: {len(updates)} files. No requests sent. Use --apply to update Dataverse.")
        return
    if not updates:
        print("No changes to apply.")
        return
    if not api_token:
        raise ValueError("Set api_token in config.ini or DATAVERSE_API_TOKEN before applying updates")
    api = DataverseAPI(server_url, api_token)
    # Validate all memberships and retrieve metadata before the first write.
    prepared = [(file_id, api.prepare(doi, file_id, changes)) for doi, file_id, changes in updates]
    for index, (file_id, metadata) in enumerate(prepared):
        try:
            api.update(file_id, metadata)
        except (ValueError, requests.RequestException) as error:
            detail = str(error) if isinstance(error, ValueError) else "Network request failed or timed out"
            detail = detail.replace(api_token, "[REDACTED]")
            raise ValueError(f"Stopped at file {file_id}; {index} updates confirmed. {detail}. Review server state before retrying.") from error
        print(f"Updated file {file_id}")
    print(f"Applied {len(prepared)} updates. Dataset publication is a separate step.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="config.ini")
    parser.add_argument("--apply", action="store_true", help="Send updates; default is offline preview")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        token = (os.getenv("DATAVERSE_API_TOKEN", "").strip()
                 or config.get("dataverse", "api_token", fallback="").strip())
        run(config["paths"]["csv_file"], config["dataverse"]["server_url"], token, args.apply)
    except requests.RequestException:
        parser.exit(1, "Error: Dataverse request failed; check connection and server settings.\n")
    except (OSError, ValueError, TypeError, AttributeError) as error:
        parser.exit(1, f"Error: {error}\n")


if __name__ == "__main__":
    main()
