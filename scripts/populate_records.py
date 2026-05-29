#!/usr/bin/env python3
"""Populate Hugo content from JSON data files.

Usage:
    python scripts/populate_records.py data/simulation_software.json software
    python scripts/populate_records.py data/cyclic_testing.json publications --force

Each record in the JSON file must include a "category" field with one of the
five main category slugs, and a "subcategory" field matching the record type
argument. Records are written to content/<category>/<subcategory>/<slug>.md.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

CATEGORIES = [
    "cyclic-testing",
    "data-repositories",
    "data-standardisation",
    "simulation",
    "system-level-testing",
]

SUBCATEGORY_TITLES = {
    "software":     "Software",
    "publications": "Publications",
    "tutorials":    "Tutorials",
    "datasets":     "Datasets",
    "other":        "Other",
}

CATEGORY_TITLES = {
    "cyclic-testing":        "Cyclic Testing",
    "data-repositories":     "Data Repositories",
    "data-standardisation":  "Data Standardisation",
    "simulation":            "Simulation",
    "system-level-testing":  "System Level Testing",
}

SUBCATEGORY_DESCS = {
    "software":     "Software tools relevant to this area",
    "publications": "Research papers and articles",
    "tutorials":    "Guides and learning resources",
    "datasets":     "Experimental and simulation datasets",
    "other":        "Other relevant resources",
}

CATEGORY_DESCS = {
    "cyclic-testing":        "Resources related to cyclic testing of batteries",
    "data-repositories":     "Repositories of battery research data",
    "data-standardisation":  "Standards, ontologies and data formats for battery data",
    "simulation":            "Battery simulation tools and models",
    "system-level-testing":  "Resources for system level battery testing",
}

RECORD_TYPES = list(SUBCATEGORY_TITLES.keys())

REQUIRED_FIELDS = {
    "software":     ["title", "description", "category", "subcategory"],
    "publications": ["title", "category", "subcategory"],
    "tutorials":    ["title", "description", "category", "subcategory"],
    "datasets":     ["title", "description", "category", "subcategory"],
    "other":        ["title", "description", "category", "subcategory"],
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


def ensure_index(directory: str, title: str, description: str, extra: dict | None = None) -> None:
    """Create a _index.md in directory if it does not exist."""
    index_path = os.path.join(directory, "_index.md")
    if os.path.exists(index_path):
        return
    lines = ["+++", f"title = {toml_value(title)}", f"description = {toml_value(description)}"]
    if extra:
        for k, v in extra.items():
            lines.append(f"{k} = {toml_value(v)}")
    lines.append("+++")
    os.makedirs(directory, exist_ok=True)
    with open(index_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Created index: {index_path}")


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

    required = REQUIRED_FIELDS.get(record_type, ["title", "category", "subcategory"])

    created = skipped = errors = 0

    for record in records:
        # Validate required fields
        missing = [f for f in required if not record.get(f)]
        if missing:
            print(
                f"Warning: skipping record — missing required fields {missing}: "
                f"{record.get('title', '<no title>')}",
                file=sys.stderr,
            )
            errors += 1
            continue

        category = record.get("category", "")
        subcategory = record.get("subcategory", record_type)

        if category not in CATEGORIES:
            print(
                f"Warning: skipping record — invalid category '{category}': "
                f"{record.get('title', '<no title>')}",
                file=sys.stderr,
            )
            errors += 1
            continue

        if subcategory not in RECORD_TYPES:
            print(
                f"Warning: skipping record — invalid subcategory '{subcategory}': "
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

        # Ensure category and subcategory _index.md files exist
        cat_dir = os.path.join(CONTENT_ROOT, category)
        ensure_index(
            cat_dir,
            CATEGORY_TITLES[category],
            CATEGORY_DESCS[category],
            {"layout": "category"},
        )
        sub_dir = os.path.join(cat_dir, subcategory)
        ensure_index(
            sub_dir,
            SUBCATEGORY_TITLES[subcategory],
            SUBCATEGORY_DESCS[subcategory],
            {"subcategory": subcategory},
        )

        outpath = os.path.join(sub_dir, f"{slug}.md")
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
        help="Subcategory type for these records",
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

