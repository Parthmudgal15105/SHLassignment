import json
from pathlib import Path
from collections import Counter

ROOT_DIR = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT_DIR / "data" / "shl_catalog.json"


def get_test_type(item):
    keys = item.get("keys", [])

    if isinstance(keys, list):
        return ",".join(keys)

    if isinstance(keys, str):
        return keys

    return ""


def main():
    if not CATALOG_PATH.exists():
        print(f"Catalog file not found: {CATALOG_PATH}")
        print("Run: python scripts/download_catalog.py")
        return

    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        catalog = json.load(f)

    print("Total items:", len(catalog))

    print("\nSample item keys:")
    print(list(catalog[0].keys()))

    print("\nFirst 10 products:")
    for item in catalog[:10]:
        print("-" * 80)
        print("Name:", item.get("name"))
        print("Link:", item.get("link"))
        print("Keys:", item.get("keys"))
        print("Duration:", item.get("duration"))
        print("Remote:", item.get("remote"))
        print("Adaptive:", item.get("adaptive"))
        print("Job Levels:", item.get("job_levels"))
        print("Languages:", item.get("languages"))

    key_counter = Counter()

    for item in catalog:
        keys = item.get("keys", [])

        if isinstance(keys, list):
            for key in keys:
                key_counter[key] += 1
        elif isinstance(keys, str):
            key_counter[keys] += 1

    print("\nAssessment key distribution:")
    for key, count in key_counter.most_common():
        print(f"{key}: {count}")

    missing_description = [
        item.get("name") for item in catalog if not item.get("description")
    ]

    print("\nItems with missing description:", len(missing_description))

    print("\nImportant trace products check:")
    important_names = [
        "Occupational Personality Questionnaire OPQ32r",
        "SHL Verify Interactive G+",
        "Graduate Scenarios",
        "Core Java (Advanced Level) (New)",
        "Spring (New)",
        "SQL (New)",
        "Docker (New)",
        "Amazon Web Services (AWS) Development (New)",
        "Smart Interview Live Coding",
        "Linux Programming (General)",
        "Networking and Implementation (New)",
        "SVAR Spoken English (US) (New)",
        "Contact Center Call Simulation (New)",
        "Financial Accounting (New)",
        "Basic Statistics (New)",
        "Dependability and Safety Instrument (DSI)",
        "Workplace Health and Safety (New)",
        "HIPAA (Security)",
        "Medical Terminology (New)",
        "Microsoft Word 365 - Essentials (New)",
        "MS Excel (New)",
        "MS Word (New)",
        "Microsoft Excel 365 (New)",
        "Microsoft Word 365 (New)",
    ]

    catalog_names = {item.get("name", "").lower(): item for item in catalog}

    for name in important_names:
        found = catalog_names.get(name.lower())
        if found:
            print(f"FOUND: {name}")
        else:
            print(f"MISSING: {name}")


if __name__ == "__main__":
    main()