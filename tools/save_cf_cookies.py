"""tools/save_cf_cookies.py
Run once manually to solve Cloudflare Turnstile and save the resulting cookies
so automated scrapers can reuse them.

Usage:
    python tools/save_cf_cookies.py
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth  # type: ignore
import json

TARGET_URL = "https://www.sahibinden.com/kiralik-daire"
COOKIE_FILE = Path("cf_cookies.json")


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        # Apply stealth evasions using the new playwright-stealth API ≥2.0
        Stealth().apply_stealth_sync(page)
        page.goto(TARGET_URL, timeout=0)

        print("⚠️  Solve the Cloudflare captcha in the opened window…")
        # Wait indefinitely until the first listing row appears
        page.wait_for_selector("tr.searchResultsItem", timeout=0)

        COOKIE_FILE.write_text(json.dumps(ctx.storage_state(path=None)), encoding="utf-8")
        print(f"✅ Cloudflare cookies saved to {COOKIE_FILE}")
        browser.close()


if __name__ == "__main__":
    main() 