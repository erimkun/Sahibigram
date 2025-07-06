"""SahibindenScraperAPI – lightweight scraper that fetches pages through
ScraperAPI's rendering service (render=true) and parses listings using
BeautifulSoup.  It requires the environment variable SCRAPERAPI_KEY and
optionally SCRAPERAPI_EXTRA_PARAMS (e.g. "country_code=tr").

Usage:
    from scraper.sahibinden_scraper_api import SahibindenScraperAPI
    scraper = SahibindenScraperAPI(max_pages=3)
    listings = scraper.run()
    print(len(listings))
"""
from __future__ import annotations

import os
import time
import random
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup  # type: ignore
from urllib.parse import urlencode, urljoin

from .config import ScraperConfig

logger = logging.getLogger("SahibindenScraperAPI")
logger.setLevel(logging.INFO)


class SahibindenScraperAPI:
    BASE_URL = "https://www.sahibinden.com/kiralik-daire"

    def __init__(self, max_pages: int | None = None, config: ScraperConfig | None = None):
        self.config = config or ScraperConfig()
        self.max_pages = max_pages or self.config.DEFAULT_MAX_PAGES
        self.api_key = os.getenv("SCRAPERAPI_KEY")
        if not self.api_key:
            raise EnvironmentError("SCRAPERAPI_KEY env var not set")
        self.extra_params = os.getenv("SCRAPERAPI_EXTRA_PARAMS", "")
        self.session = requests.Session()
        self.stats: Dict[str, Any] = {
            "total_pages_scraped": 0,
            "total_listings_found": 0,
        }

    # ---------------------------------------------------------------------
    # HTTP helpers
    # ---------------------------------------------------------------------

    def _scraperapi_url(self, target_url: str) -> str:
        params = {
            "api_key": self.api_key,
            "url": target_url,
            "render": "true",
            "wait_for_selector": ScraperConfig.SELECTORS["listing_container"],
        }
        if self.extra_params:
            # parse key1=val1,key2=val2 style
            for kv in self.extra_params.split(","):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    params[k.strip()] = v.strip()
        return f"https://api.scraperapi.com/?{urlencode(params)}"

    def _fetch_page(self, page_num: int) -> str | None:
        target = f"{self.BASE_URL}?page={page_num}"
        api_url = self._scraperapi_url(target)
        logger.debug("Fetching %s", api_url)
        try:
            resp = self.session.get(api_url, timeout=120)
            resp.raise_for_status()
            return resp.text
        except Exception as exc:
            logger.error("HTTP error on page %s: %s", page_num, exc)
            return None

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------

    def _parse_listings(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select(ScraperConfig.SELECTORS["listing_container"])
        results: List[Dict[str, Any]] = []
        for row in rows:
            try:
                title_el = row.select_one(ScraperConfig.SELECTORS["title"])
                price_el = row.select_one(ScraperConfig.SELECTORS["price"])
                location_el = row.select_one(ScraperConfig.SELECTORS["location"])
                date_el = row.select_one(ScraperConfig.SELECTORS["date"])
                url_el = row.select_one(ScraperConfig.SELECTORS["url"])
                image_el = row.select_one(ScraperConfig.SELECTORS["image"])

                title = title_el.get_text(strip=True) if title_el else None
                price = price_el.get_text(strip=True) if price_el else None
                location = location_el.get_text(strip=True) if location_el else None
                date = date_el.get_text(strip=True) if date_el else None

                rel_url = url_el["href"] if url_el and url_el.has_attr("href") else None
                full_url = urljoin(self.BASE_URL, rel_url) if rel_url else None
                image_url = image_el["src"] if image_el and image_el.has_attr("src") else None

                if title and price and location:
                    results.append(
                        {
                            "title": title,
                            "price": price,
                            "location": location,
                            "date": date,
                            "url": full_url,
                            "image_url": image_url,
                            "scraped_at": time.time(),
                        }
                    )
            except Exception as parse_exc:
                logger.debug("Parse error: %s", parse_exc)
                continue
        return results

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def run(self) -> List[Dict[str, Any]]:
        all_listings: List[Dict[str, Any]] = []
        for page in range(1, self.max_pages + 1):
            logger.info("Scraping page %s/%s via ScraperAPI", page, self.max_pages)
            html = self._fetch_page(page)
            if not html:
                logger.warning("No HTML returned for page %s", page)
                break
            listings = self._parse_listings(html)
            if not listings:
                logger.info("No listings found on page %s – stopping", page)
                break
            all_listings.extend(listings)
            self.stats["total_pages_scraped"] += 1
            self.stats["total_listings_found"] += len(listings)
            # polite delay
            time.sleep(random.uniform(self.config.MIN_DELAY, self.config.MAX_DELAY))
        logger.info("Completed. Found %s listings", len(all_listings))
        return all_listings

    # ------------------------------------------------------------------
    # Export helpers (reuse JSON/CSV export from main scraper)
    # ------------------------------------------------------------------

    def export(self, data: List[Dict[str, Any]], fmt: str = "json") -> Path:
        stamp = time.strftime("%Y%m%d_%H%M%S")
        export_dir = Path(self.config.EXPORT_DIRECTORY)
        export_dir.mkdir(exist_ok=True)
        filename = export_dir / f"sahibinden_api_{stamp}.{fmt}"
        if fmt == "json":
            filename.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        elif fmt == "csv":
            import pandas as pd  # local import

            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
        else:
            raise ValueError("Unsupported format: " + fmt)
        logger.info("Exported data to %s", filename)
        return filename 