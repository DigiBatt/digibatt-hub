#!/usr/bin/env python3
"""
Harvest metadata records from the Zenodo Digibatt community using the REST API.

Usage
-----
    python harvest_zenodo.py [--output-dir OUTPUT_DIR] [--token TOKEN]

Requirements
------------
    pip install requests
"""

import argparse
import json
import logging
import sys
from pathlib import Path

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

API_ENDPOINT = "https://zenodo.org/api/records"
COMMUNITY = "digibatt"
DEFAULT_OUTPUT_DIR = "data/zenodo"
PAGE_SIZE = 25

RESOURCE_TYPE_MAP = {
    "article": "Publication",
    "publication": "Publication",
    "conferencepaper": "Publication",
    "preprint": "Publication",
    "thesis": "Publication",
    "report": "Publication",
    "book": "Publication",
    "bookpart": "Publication",
    "workingpaper": "Publication",
    "dataset": "Dataset",
    "software": "Software",
    "image": "Image",
    "video": "Video",
    "audio": "Audio",
    "lesson": "Lesson",
    "poster": "Poster",
    "presentation": "Presentation",
    "other": "Other",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def _get_resource_type(record: dict) -> str:
    try:
        rtype = record["metadata"]["resource_type"]["type"].lower()
        return RESOURCE_TYPE_MAP.get(rtype, "Other")
    except KeyError:
        return "Other"


def harvest(output_dir: Path, token: str | None = None) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    total = 0

    params = {
        "communities": COMMUNITY,
        "size": PAGE_SIZE,
        "page": 1,
        "sort": "mostrecent",
    }
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    log.info("Starting harvest from %s (community=%s) …", API_ENDPOINT, COMMUNITY)

    while True:
        resp = requests.get(API_ENDPOINT, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        hits = data.get("hits", {}).get("hits", [])
        if not hits:
            break

        for record in hits:
            resource_type = _get_resource_type(record)
            record_id = str(record["id"])

            folder = output_dir 
            folder.mkdir(exist_ok=True)
            filepath = folder / f"{record_id}.json"

            filepath.write_text(
                json.dumps(record, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            total += 1

        log.info("Page %d: fetched %d records (total so far: %d)", params["page"], len(hits), total)

        # Check if there are more pages
        if len(hits) < PAGE_SIZE:
            break
        params["page"] += 1

    log.info("Harvest complete. %d record(s) saved to '%s'.", total, output_dir)
    return total


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Harvest metadata from the Zenodo Digibatt community via REST API."
    )
    parser.add_argument(
        "--output-dir",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Root directory for saved records (default: '{DEFAULT_OUTPUT_DIR}')",
    )
    parser.add_argument(
        "--token",
        default=None,
        help="Zenodo personal access token (optional, increases rate limits)",
    )
    args = parser.parse_args()
    try:
        harvest(Path(args.output_dir), token=args.token)
    except Exception as exc:  # noqa: BLE001
        log.error("Fatal error: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()