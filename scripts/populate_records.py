#!/usr/bin/env python3
"""Populate Hugo content from JSON data files.

Usage:
    python scripts/populate_records.py data/software.json software
    python scripts/populate_records.py data/publications.json publications --force
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

RECORD_TYPES = ["software", "publications", "datasets", "databases", "tutorials"]

REQUIRED_FIELDS = {
    "software":     ["title", "description"],
    "publications": ["title"],
    "datasets":     ["title", "description"],
    "databases":    ["title", "description"],
    "tutorials":    ["title", "description"],
}

CONTENT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "content")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def toml_value(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        # Use single-quoted strings; escape backslash and single-quote
        escaped = v.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, list):
        items = ", ".join(toml_value(i) for i in v)
        return f"[{items}]"
    if v is None:
        return "''"
    return f"'{v}'"


def build_frontmatter(record: dict, record_type: str) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "+++",
        f"title = {toml_value(record.get('title', ''))}",
        f"date = '{now}'",
        "draft = false",
        f"type = '{record_type}'",
    ]
    skip = {"title", "body"}
    for k, v in record.items():
        if k in skip:
            continue
        lines.append(f"{k} = {toml_value(v)}")
    lines.append("+++")
    return "\n".join(lines)


def populate(json_path: str, record_type: str, force: bool = False) -> None:
    if not os.path.exists(json_path):
        sys.exit(f"Error: JSON file not found: {json_path}")

    with open(json_path, encoding="utf-8") as f:
        try:
            records = json.load(f)
        except json.JSONDecodeError as e:
            sys.exit(f"Error: Invalid JSON in {json_path}: {e}")

    if not isinstance(records, list):
        sys.exit("Error: JSON file must contain an array of record objects.")

    required = REQUIRED_FIELDS.get(record_type, ["title"])
    output_dir = os.path.join(CONTENT_ROOT, record_type)
    os.makedirs(output_dir, exist_ok=True)

    created = skipped = errors = 0

    for record in records:
        missing = [f for f in required if not record.get(f)]
        if missing:
            print(
                f"Warning: skipping record — missing required fields {missing}: "
                f"{record.get('title', '<no title>')}",
                file=sys.stderr,
            )
            errors += 1
            continue

        slug = slugify(record["title"])
        if not slug:
            print("Warning: could not derive slug from title, skipping.", file=sys.stderr)
            errors += 1
            continue

        outpath = os.path.join(output_dir, f"{slug}.md")
        if os.path.exists(outpath) and not force:
            print(f"Skipping (exists): {outpath}")
            skipped += 1
            continue

        fm = build_frontmatter(record, record_type)
        body = record.get("body", "")
        content = f"{fm}\n{body}\n" if body else f"{fm}\n"

        with open(outpath, "w", encoding="utf-8") as out:
            out.write(content)
        print(f"Created: {outpath}")
        created += 1

    print(f"\nDone — created: {created}, skipped: {skipped}, errors: {errors}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Populate Hugo content from a JSON data file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("json_file", help="Path to the JSON data file (array of records)")
    parser.add_argument(
        "record_type",
        choices=RECORD_TYPES,
        help="Record type (must match a content section directory)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing .md files",
    )
    args = parser.parse_args()
    populate(args.json_file, args.record_type, args.force)


if __name__ == "__main__":
    main()
