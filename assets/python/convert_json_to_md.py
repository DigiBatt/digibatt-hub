import json
import sys
import re
from pathlib import Path
from datetime import datetime, timezone


def parse_archetype(archetype_path: Path) -> list[str]:
    """Extract field names from a TOML frontmatter archetype .md file."""
    text = archetype_path.read_text()
    # Extract content between +++ delimiters
    match = re.search(r'\+\+\+(.*?)\+\+\+', text, re.DOTALL)
    if not match:
        return []
    frontmatter = match.group(1)
    # Extract field names (left side of = )
    fields = re.findall(r'^\s*(\w+)\s*=', frontmatter, re.MULTILINE)
    # Remove meta fields handled separately
    skip = {"date", "title", "draft"}
    return [f for f in fields if f not in skip]


def load_archetypes(archetypes_dir: str = "archetypes") -> dict:
    """Load all archetypes from .md files in the archetypes directory."""
    archetypes = {}
    for path in Path(archetypes_dir).glob("*.md"):
        name = path.stem
        if name == "default":
            continue
        archetypes[name] = parse_archetype(path)
    return archetypes


CONTENT_DIR_MAP = {
    "software": "content/simulation/software",
    "publications": "content/publications",
    "tutorials": "content/tutorials",
    "datasets": "content/data-repositories/datasets",
    "other": "content/other",
}


def to_toml_value(value):
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


def convert(input_path: str, output_dir: str = None, archetypes_dir: str = "archetypes"):
    with open(input_path) as f:
        data = json.load(f)

    archetypes = load_archetypes(archetypes_dir)

    # Determine type from 'type' or 'subcategory'
    record_type = data.get("type") or data.get("subcategory", "other")

    if record_type not in archetypes:
        print(f"Warning: no archetype found for '{record_type}', falling back to 'other'")
        record_type = "other"

    fields = archetypes.get(record_type, [])

    slug = Path(input_path).stem
    date = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    title = data.get("title", slug)

    # Build frontmatter lines
    lines = ["+++"]
    lines.append(f"title = '{title.replace(chr(39), chr(39)*2)}'")
    lines.append(f"date = '{date}'")
    lines.append("draft = false")

    for field in fields:
        val = data.get(field)
        if val is not None:
            lines.append(f"{field} = {to_toml_value(val)}")
        else:
            if field == "authors":
                lines.append(f"{field} = []")
            else:
                lines.append(f"{field} = ''")

    lines.append("+++")

    body = data.get("description", "")
    content = "\n".join(lines) + "\n\n" + body + "\n"

    if output_dir is None:
        output_dir = CONTENT_DIR_MAP.get(record_type, f"content/{record_type}")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{slug}.md"
    out_file.write_text(content)
    print(f"Written to {out_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python convert_json_to_md.py <input.json> [output_dir] [archetypes_dir]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_directory = sys.argv[2] if len(sys.argv) > 2 else None
    archetypes_directory = sys.argv[3] if len(sys.argv) > 3 else "archetypes"
    convert(input_file, output_directory, archetypes_directory)