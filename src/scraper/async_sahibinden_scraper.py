"""
⚡ AsyncSahibindenScraper – concurrent Playwright scraper for sahibinden.com
Phase 2: production-grade scraping engine – step 1 (concurrency).
Built on top of the proven sync `SahibindenScraper` logic, but utilises
`playwright.async_api` and asyncio tasks to fetch multiple result pages in parallel.

Usage example:
```python
import asyncio
from scraper.async_sahibinden_scraper import AsyncSahibindenScraper

async def main():
    async with AsyncSahibindenScraper(max_concurrency=5) as scraper:
        listings = await scraper.scrape_pages(
            base_url="https://www.sahibinden.com/kiralik-daire",
            max_pages=50
        )
        await scraper.export_data(listings, "results_async.json")

asyncio.run(main())
```
"""

from __future__ import annotations

import asyncio
import json
import logging
import random
import time
from typing import List, Dict, Optional
from urllib.parse import urljoin
from pathlib import Path
import os

from playwright.async_api import async_playwright, Page, BrowserContext  # type: ignore
from playwright_stealth import Stealth  # type: ignore

from .config import ScraperConfig


class AsyncSahibindenScraper:
    """Asynchronous, concurrent scraper for sahibinden.com."""

    def __init__(self, config: Optional[ScraperConfig] = None, *, max_concurrency: int = 5) -> None:
        self.config = config or ScraperConfig()
        self.max_concurrency = max_concurrency

        # Playwright handles
        self._playwright = None
        self._browser = None
        self._context: BrowserContext | None = None

        # Logging
        self.logger = logging.getLogger("AsyncSahibindenScraper")
        self.logger.setLevel(self.config.LOG_LEVEL)

        # Statistics
        self.stats: Dict[str, int] = {
            "total_pages_scraped": 0,
            "total_listings_found": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
        }

        # Concurrency primitives
        self._sem = asyncio.Semaphore(max_concurrency)

    # ---------------------------------------------------------------------
    # Async context-manager helpers
    # ---------------------------------------------------------------------
    async def __aenter__(self) -> "AsyncSahibindenScraper":
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop_browser()

    # ---------------------------------------------------------------------
    # Browser lifecycle
    # ---------------------------------------------------------------------
    async def start_browser(self):
        """Initialise Playwright browser + context."""
        if self._browser:
            return
        self._playwright = await async_playwright().start()
        cookie_file = Path("cf_cookies.json")
        storage_state = str(cookie_file) if cookie_file.exists() else None
        launch_kwargs = {"headless": self.config.HEADLESS}
        proxy_server = os.getenv("SAHIBI_PROXY")
        if proxy_server:
            launch_kwargs["proxy"] = {"server": proxy_server}  # type: ignore[arg-type]

        self._browser = await self._playwright.chromium.launch(**launch_kwargs)
        self._context = await self._browser.new_context(storage_state=storage_state, **self.config.get_context_options())

        # Apply stealth evasions to the entire browser context (playwright-stealth ≥2.0)
        await Stealth().apply_stealth_async(self._context)

        self.logger.info("Browser started (async, headless=%s)", self.config.HEADLESS)

    async def stop_browser(self):
        """Cleanup Playwright objects."""
        try:
            if self._context:
                await self._context.close()
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
            self.logger.info("Browser stopped successfully")
        except Exception as exc:
            self.logger.error("Error while closing browser: %s", exc)

    # ---------------------------------------------------------------------
    # Random delay util
    # ---------------------------------------------------------------------
    async def _random_delay(self):
        delay = random.uniform(self.config.MIN_DELAY, self.config.MAX_DELAY)
        await asyncio.sleep(delay)

    # ---------------------------------------------------------------------
    # Extraction logic (adapted from sync version)
    # ---------------------------------------------------------------------
    async def _extract_page(self, page_num: int, base_url: str) -> List[Dict]:
        """Fetch and parse a single result page."""
        url = f"{base_url}?page={page_num}"
        async with self._sem:  # concurrency limiter
            assert self._context is not None, "Browser context not initialized. Call start_browser() first."
            page: Page = await self._context.new_page()
            try:
                await page.goto(url, timeout=self.config.PAGE_TIMEOUT)
                await page.wait_for_selector(self.config.SELECTORS["listing_container"], timeout=self.config.PAGE_TIMEOUT)

                listings = await page.query_selector_all(self.config.SELECTORS["listing_container"])
                extracted: List[Dict] = []

                for listing in listings:
                    try:
                        title_el = await listing.query_selector(self.config.SELECTORS["title"])
                        price_el = await listing.query_selector(self.config.SELECTORS["price"])
                        loc_el = await listing.query_selector(self.config.SELECTORS["location"])
                        date_el = await listing.query_selector(self.config.SELECTORS["date"])
                        url_el = await listing.query_selector(self.config.SELECTORS["url"])
                        img_el = await listing.query_selector(self.config.SELECTORS["image"])

                        title = (await title_el.inner_text()) if title_el else None
                        price = (await price_el.inner_text()) if price_el else None
                        location = (await loc_el.inner_text()) if loc_el else None
                        date = (await date_el.inner_text()) if date_el else None

                        rel = await url_el.get_attribute("href") if url_el else None
                        full_url = urljoin(self.config.BASE_URL, rel) if rel else None
                        image_url = await img_el.get_attribute("src") if img_el else None

                        listing_data = {
                            "title": title.strip() if title else None,
                            "price": price.strip() if price else None,
                            "location": location.strip() if location else None,
                            "date": date.strip() if date else None,
                            "url": full_url,
                            "image_url": image_url,
                            "scraped_at": time.time(),
                        }

                        if title and price and location:
                            extracted.append(listing_data)
                            self.stats["successful_extractions"] += 1
                        else:
                            self.stats["failed_extractions"] += 1
                    except Exception as item_err:
                        self.stats["failed_extractions"] += 1
                        self.logger.debug("Item extraction error on page %s: %s", page_num, item_err)

                self.logger.info("Page %s: %s listings", page_num, len(extracted))
                self.stats["total_pages_scraped"] += 1
                self.stats["total_listings_found"] += len(extracted)
                return extracted
            except Exception as page_err:
                self.logger.warning("Failed to scrape page %s: %s", page_num, page_err)
                return []
            finally:
                await page.close()
                await self._random_delay()

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    async def scrape_pages(self, *, base_url: str, max_pages: int = 5) -> List[Dict]:
        """Scrape multiple pages concurrently."""
        if not self._browser:
            await self.start_browser()

        tasks = [asyncio.create_task(self._extract_page(page_num, base_url)) for page_num in range(1, max_pages + 1)]
        results_nested = await asyncio.gather(*tasks)
        # Flatten
        listings: List[Dict] = [item for sub in results_nested for item in sub]
        return listings

    # ---------------------------------------------------------------------
    # Export utilities (JSON / CSV, sync for simplicity)
    # ---------------------------------------------------------------------
    async def export_data(self, data: List[Dict], filename: str, fmt: str = "json") -> bool:
        """Export listings to a file (blocking I/O wrapped in thread-executor)."""
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._export_sync, data, filename, fmt)

    def _export_sync(self, data: List[Dict], filename: str, fmt: str) -> bool:
        try:
            if fmt == "json":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif fmt == "csv":
                import csv
                if data:
                    with open(filename, "w", newline="", encoding="utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            self.logger.info("Data exported → %s (%s)", filename, fmt)
            return True
        except Exception as exc:
            self.logger.error("Export failed: %s", exc)
            return False 