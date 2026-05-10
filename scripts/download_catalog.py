import json
import requests
from pathlib import Path

CATALOG_URL = "https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json"

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_PATH = DATA_DIR / "raw_catalog.json"
CLEAN_PATH = DATA_DIR / "shl_catalog.json"


def main():
    DATA_DIR.mkdir(exist_ok=True)

    print("Downloading SHL catalogue...")

    response = requests.get(CATALOG_URL, timeout=30)
    response.raise_for_status()

    raw_text = response.text

    # Save raw file for debugging
    RAW_PATH.write_text(raw_text, encoding="utf-8")

    try:
        # strict=False allows control characters inside strings
        catalog = json.loads(raw_text, strict=False)
    except json.JSONDecodeError as e:
        print("JSON decode failed.")
        print(f"Error: {e}")
        print(f"Line: {e.lineno}, Column: {e.colno}, Position: {e.pos}")

        start = max(e.pos - 200, 0)
        end = min(e.pos + 200, len(raw_text))
        print("\nProblem area:")
        print(raw_text[start:end])

        return

    CLEAN_PATH.write_text(
        json.dumps(catalog, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    if isinstance(catalog, list):
        print(f"Downloaded {len(catalog)} catalogue items.")
    elif isinstance(catalog, dict):
        print(f"Downloaded catalogue with keys: {list(catalog.keys())}")

    print(f"Saved cleaned catalogue to: {CLEAN_PATH}")


if __name__ == "__main__":
    main()