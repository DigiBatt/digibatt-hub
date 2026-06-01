import json
from pathlib import Path

def convert_zenodo_to_dataset(zenodo_path: str, output_path: str = None):
    with open(zenodo_path) as f:
        zenodo = json.load(f)

    meta = zenodo.get("metadata", {})

    # Map creators to authors list
    authors = [c["name"] for c in meta.get("creators", [])]

    # Get category from communities or keywords — default to data-repositories
    category = "data-repositories"

    dataset = {
        "title": zenodo.get("title", ""),
        "description": _strip_html(meta.get("description", "")),
        "category": category,
        "subcategory": "datasets",
        "url": zenodo.get("links", {}).get("self_html", ""),
        "format": _get_formats(zenodo.get("files", [])),
        "license": meta.get("license", {}).get("id", ""),
        "authors": authors,
    }

    if output_path:
        with open(output_path, "w") as f:
            json.dump(dataset, f, indent=2)
        print(f"Written to {output_path}")
    else:
        print(json.dumps(dataset, indent=2))

    return dataset


def _strip_html(text: str) -> str:
    """Very basic HTML tag stripper."""
    import re
    clean = re.sub(r"<[^>]+>", "", text)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def _get_formats(files: list) -> str:
    """Extract unique file extensions from file list."""
    extensions = set()
    for f in files:
        key = f.get("key", "")
        ext = Path(key).suffix.lstrip(".").upper()
        if ext:
            extensions.add(ext)
    return ", ".join(sorted(extensions))


if __name__ == "__main__":
    import sys

    input_file = sys.argv[1] if len(sys.argv) > 1 else "data/zenodo/Dataset/18986774.json"
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    convert_zenodo_to_dataset(input_file, output_file)