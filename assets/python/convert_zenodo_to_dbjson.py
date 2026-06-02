import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone


ZENODO_DIR = Path("data/zenodo")
SCHEMAS_DIR = Path("schemas")
OUTPUT_DIR = Path("data/uncategorised")

# Map Zenodo resource_type to schema file
RESOURCE_TYPE_MAP = {
    "software": "software.json",
    "dataset": "datasets.json",
    "publication": "publications.json",
    "other": "other.json",
}


def load_schema(resource_type: str) -> dict:
    schema_file = RESOURCE_TYPE_MAP.get(resource_type)
    if not schema_file:
        print(f"  Warning: no schema for resource_type '{resource_type}', using other.json")
        schema_file = "other.json"
    schema_path = SCHEMAS_DIR / schema_file
    if not schema_path.exists():
        print(f"  Warning: schema file {schema_path} not found, skipping validation")
        return {}
    with open(schema_path) as f:
        return json.load(f)


def get_schema_fields(schema: dict) -> dict:
    """Return field names and their types/defaults from schema properties."""
    return schema.get("properties", {})


def strip_html(text: str) -> str:
    clean = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", clean).strip()


def get_formats(files: list) -> list:
    extensions = set()
    for f in files:
        ext = Path(f.get("key", "")).suffix.lstrip(".").upper()
        if ext:
            extensions.add(ext)
    return sorted(extensions)


def zenodo_to_db_record(zenodo: dict, resource_type: str, schema: dict) -> dict:
    """Map a Zenodo record to a db_record matching the schema."""
    meta = zenodo.get("metadata", {})
    fields = get_schema_fields(schema)

    authors = [c["name"] for c in meta.get("creators", [])]
    description = strip_html(meta.get("description", ""))
    formats = get_formats(zenodo.get("files", []))
    url = zenodo.get("links", {}).get("self_html", "")
    license_id = meta.get("license", {}).get("id", "")

    # Build record with defaults for all schema fields
    record = {}
    for field, props in fields.items():
        field_type = props.get("type", "string")
        if field_type == "array":
            record[field] = []
        elif field_type == "boolean":
            record[field] = False
        else:
            record[field] = ""

    # Populate known fields
    record.update({
        "title": zenodo.get("title", ""),
        "description": description,
        "category": "",           # left blank for manual categorisation
        "subcategory": resource_type,
        "url": url,
        "license": license_id,
        "authors": authors,
    })

    if "format" in fields:
        record["format"] = ", ".join(formats)

    if "repo" in fields:
        record["repo"] = url

    if "language" in fields:
        record["language"] = ", ".join(meta.get("programming_language", []))

    if "version" in fields:
        record["version"] = meta.get("version", "")

    if "doi" in fields:
        record["doi"] = meta.get("doi", "")

    if "year" in fields:
        pub_date = meta.get("publication_date", "")
        record["year"] = pub_date[:4] if pub_date else ""

    if "journal" in fields:
        record["journal"] = meta.get("journal", {}).get("title", "")

    return record


def process_zenodo_record(zenodo_path: Path):
    with open(zenodo_path) as f:
        zenodo = json.load(f)

    resource_type = zenodo.get("metadata", {}).get("resource_type", {}).get("type", "other")
    print(f"Processing {zenodo_path.name} — type: {resource_type}")

    schema = load_schema(resource_type)
    record = zenodo_to_db_record(zenodo, resource_type, schema)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / zenodo_path.name
    with open(out_file, "w") as f:
        json.dump(record, f, indent=2)
    print(f"  Saved to {out_file}")


def main():
    if not ZENODO_DIR.exists():
        print(f"Zenodo data directory '{ZENODO_DIR}' not found.")
        sys.exit(1)

    zenodo_files = list(ZENODO_DIR.rglob("*.json"))
    if not zenodo_files:
        print(f"No JSON files found in {ZENODO_DIR}")
        sys.exit(0)

    print(f"Found {len(zenodo_files)} Zenodo records\n")
    for path in zenodo_files:
        process_zenodo_record(path)

    print(f"\nDone. {len(zenodo_files)} records written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()