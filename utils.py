"""Shared configuration and UTF-8 file helpers."""
import configparser
import csv
import json
from pathlib import Path


def load_config(filepath="config.ini"):
    path = Path(filepath).resolve()
    config = configparser.ConfigParser(interpolation=None)
    if not config.read(path, encoding="utf-8"):
        raise ValueError("Configuration missing. Copy config.sample.ini to config.ini first.")
    for section, keys in {"dataverse": ["server_url"], "paths": ["json_input_dir", "csv_file"]}.items():
        for key in keys:
            if not config.get(section, key, fallback="").strip():
                raise ValueError(f"Missing configuration: [{section}] {key}")
    for key in ("json_input_dir", "csv_file"):
        config["paths"][key] = str((path.parent / config["paths"][key]).resolve())
    return config


def load_json_file(filepath):
    with open(filepath, encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{filepath}: expected a JSON object")
    return data


def load_csv_file(filepath):
    with open(filepath, encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"DOI", "file_id", "new_description", "new_file_path"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError("CSV must include DOI, file_id, new_description, new_file_path")
        rows = list(reader)
    if any(None in row or any(value is None for value in row.values()) for row in rows):
        raise ValueError("CSV has rows with missing or extra cells")
    return rows


def save_csv_file(rows, filepath, fieldnames):
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
