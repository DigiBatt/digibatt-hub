import json
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone
from jsonschema import Draft7Validator


UNCONVERTED_DIR = Path("data/submitted")
CONVERTED_DIR = Path("data/accepted")
ARCHETYPES_DIR = Path("archetypes")
CONTENT_DIR = Path("content")


def parse_archetype(archetype_path: Path) -> list[str]:
    """Extract field names from a TOML frontmatter archetype .md file."""
    text = archetype_path.read_text()
    match = re.search(r'\+\+\+(.*?)\+\+\+', text, re.DOTALL)
    if not match:
        return []
    frontmatter = match.group(1)
    fields = re.findall(r'^\s*(\w+)\s*=', frontmatter, re.MULTILINE)
    skip = {"date", "title", "draft"}
    return [f for f in fields if f not in skip]


def load_archetypes() -> dict:
    """Load all archetypes from archetypes/*.md"""
    archetypes = {}
    for path in ARCHETYPES_DIR.glob("*.md"):
        if path.stem == "default":
            continue
        archetypes[path.stem] = parse_archetype(path)
    return archetypes


def to_toml_value(value) -> str:
    if isinstance(value, list):
        items = ", ".join(f"'{v}'" for v in value)
        return f"[{items}]"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

def validate(data, subcategory):

    schema = "schemas/" + subcategory + ".json"
    print(schema)
    print("scheming")
    schemadata = json.load(open(schema))
 
    validator = Draft7Validator(schemadata)
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)

    if errors:
        for error in errors:
            print(f"❌ Error at {list(error.path)}: {error.message}")
            sys.exit("Invalid JSON file")
    else:
        print("✅ JSON is valid")


def convert(json_path: Path, archetypes: dict):
    with open(json_path) as f:
        data = json.load(f)

    category = data.get("category", "").strip()
    subcategory = data.get("subcategory", "").strip()

    if not category:
        print(f"  Skipping {json_path.name} — no category set")
        return
    if not subcategory:
        print(f"  Skipping {json_path.name} — no subcategory set")
        return

    # Validate against schema
    validate(data, subcategory)

    # Find matching archetype
    if subcategory not in archetypes:
        print(f"  Warning: no archetype for '{subcategory}', falling back to 'other'")
        subcategory_key = "other"
    else:
        subcategory_key = subcategory

    fields = archetypes.get(subcategory_key, [])

    slug = json_path.stem
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    title = data.get("title", slug)

    # Build frontmatter
    lines = ["+++"]
    lines.append(f"title = '{title.replace(chr(39), chr(39)*2)}'")
    lines.append(f"date = '{date}'")
    lines.append("draft = false")

    for field in fields:
        field = field.lower()
        val = data.get(field)
        if val is not None and val != "":
            lines.append(f"{field} = {to_toml_value(val)}")
        else:
            if field == "authors":
                lines.append(f"{field} = []")
            else:
                lines.append(f"{field} = ''")

    lines.append("+++")

    body = data.get("description", "")
    content = "\n".join(lines) + "\n\n" + body + "\n"

    # Write to content/category/subcategory/slug.md
    out_dir = CONTENT_DIR / category / subcategory
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{slug}.md"
    out_file.write_text(content)
    print(f"  Written to {out_file}")


def moveconverted(json_path: Path, overwrite: bool = True):
    """Move converted JSON file to the converted directory."""
    
    if not CONVERTED_DIR.exists():
        print(f"Directory '{CONVERTED_DIR}' not found.")
        sys.exit(1)

    converted_file = CONVERTED_DIR / json_path.name
    
    if converted_file.exists():
        if not overwrite:
            print(f"  Warning: {converted_file} already exists, skipping move")
            return
        else:
            converted_file.unlink()
            print(f"  Overwriting existing file")
    
    shutil.move(str(json_path), str(converted_file))
    print(f"  Moved to {converted_file}")



def main():
    if not UNCONVERTED_DIR.exists():
        print(f"Directory '{UNCONVERTED_DIR}' not found.")
        sys.exit(1)

    json_files = list(UNCONVERTED_DIR.rglob("*.json"))
    if not json_files:
        print(f"No JSON files found in {UNCONVERTED_DIR}")
        sys.exit(0)

    archetypes = load_archetypes()
    print(f"Loaded archetypes: {list(archetypes.keys())}")
    print(f"Found {len(json_files)} records\n")

    for path in json_files:
        print(f"Processing {path.name}")
        convert(path, archetypes)
        moveconverted(path)

    print(f"\nDone. {len(json_files)} records processed.")


if __name__ == "__main__":
    main()