"""example_async.py – Demonstration of the asynchronous concurrent scraper.

Run with:
    python -m asyncio example_async.py
or simply:
    python example_async.py

It scrapes the first 10 pages of rental apartments concurrently and
exports results to `exports/results_async.json`.
"""

import sys
from pathlib import Path
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "src"))

import asyncio
from scraper import AsyncSahibindenScraper  # type: ignore # noqa: E402

EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


async def main():
    async with AsyncSahibindenScraper(max_concurrency=5) as scraper:
        listings = await scraper.scrape_pages(
            base_url="https://www.sahibinden.com/kiralik-daire",
            max_pages=10,
        )
        await scraper.export_data(listings, EXPORT_DIR / "results_async.json")
        print(f"Scraped {len(listings)} listings → exports/results_async.json")
        print("Stats:", scraper.stats)


if __name__ == "__main__":
    asyncio.run(main()) 