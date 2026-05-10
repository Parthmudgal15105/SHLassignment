import json
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT_DIR / "data" / "shl_catalog.json"


def load_catalog() -> list[dict[str, Any]]:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(
            f"Catalog file not found at {CATALOG_PATH}. "
            "Run: python scripts/download_catalog.py"
        )

    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        catalog = json.load(f)

    if not isinstance(catalog, list):
        raise ValueError("Expected catalog JSON to be a list of products.")

    return catalog


def normalize_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, list):
        return " ".join(str(x) for x in value)

    if isinstance(value, dict):
        return " ".join(f"{k} {v}" for k, v in value.items())

    return str(value)


def get_product_name(item: dict[str, Any]) -> str:
    name = normalize_text(item.get("name")).strip()
    name = " ".join(name.split())

    url = get_product_url(item)

    url_name_overrides = {
        "microsoft-excel-365-new": "Microsoft Excel 365 (New)",
        "microsoft-word-365-new": "Microsoft Word 365 (New)",
        "microsoft-word-365-essentials-new": "Microsoft Word 365 - Essentials (New)",
        "microsoft-excel-365-essentials-new": "Microsoft Excel 365 - Essentials (New)",
    }

    for slug, clean_name in url_name_overrides.items():
        if slug in url:
            return clean_name

    return name


def get_product_url(item: dict[str, Any]) -> str:
    return normalize_text(item.get("link")).strip()


def get_test_type(item: dict[str, Any]) -> str:
    keys = item.get("keys", [])

    if isinstance(keys, list):
        return ",".join(str(k) for k in keys)

    return normalize_text(keys).strip()


def make_search_text(item: dict[str, Any]) -> str:
    parts = [
        item.get("name"),
        item.get("description"),
        item.get("keys"),
        item.get("job_levels"),
        item.get("languages"),
        item.get("duration"),
    ]

    return " ".join(normalize_text(part) for part in parts).lower()