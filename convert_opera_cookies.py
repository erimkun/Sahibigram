# convert_opera_cookies.py
"""Convert Opera / Chrome DevTools TSV cookie export to Playwright storage_state JSON.

Usage (from project root):
    python3 convert_opera_cookies.py

All *.tsv files inside the ./data directory will be scanned. Only cookies
whose Domain column contains "sahibinden.com" are kept. The resulting
storage state is written to `cf_cookies.json`, which the scrapers already
load automatically.
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Dict, Any

DATA_DIR = Path("data")
OUTPUT_FILE = Path("cf_cookies.json")

state: Dict[str, Any] = {"cookies": [], "origins": []}

if not DATA_DIR.exists():
    raise SystemExit("❌ data/ directory not found. Place your *.tsv exports inside a 'data' folder.")

FIELDNAMES = [
    "Name", "Value", "Domain", "Path", "Expires/Max-Age", "Size",
    "HttpOnly", "Secure", "SameSite", "Partition Key Site", "Cross Site", "Priority",
]

for tsv_path in DATA_DIR.glob("*.tsv"):
    with tsv_path.open(newline="", encoding="utf-8") as fh:
        # Detect if the first line is header; if not, use predefined fieldnames
        peek = fh.readline()
        fh.seek(0)
        if peek.startswith("Name\t"):
            reader = csv.DictReader(fh, delimiter="\t")
        else:
            reader = csv.DictReader(fh, delimiter="\t", fieldnames=FIELDNAMES)
        for row in reader:
            if "sahibinden.com" not in row["Domain"]:
                continue  # skip irrelevant domains

            # Convert expiry: Opera shows ISO timestamp or blank for session cookies
            exp_raw = row["Expires/Max-Age"].strip()
            if exp_raw and exp_raw != "Session":
                # take only the date part to avoid locale issues
                exp_struct = time.strptime(exp_raw.split("T")[0], "%Y-%m-%d")
                expires = int(time.mktime(exp_struct))
            else:
                expires = -1  # session cookie

            state["cookies"].append({
                "name": row["Name"],
                "value": row["Value"],
                "domain": row["Domain"].lstrip("."),
                "path": row.get("Path", "/") or "/",
                "expires": expires,
                "httpOnly": row.get("HttpOnly", "") == "✓",
                "secure": row.get("Secure", "") == "✓",
                "sameSite": row.get("SameSite", "Lax") or "Lax",
            })

if not state["cookies"]:
    raise SystemExit("❌ No sahibinden.com cookies found in ./data/*.tsv — make sure you exported the right tab.")

OUTPUT_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
print(f"✅ Wrote {OUTPUT_FILE} with {len(state['cookies'])} cookies") 