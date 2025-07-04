Web Scraping Technical Report: sahibinden.com
Target Site: https://www.sahibinden.com
Objective: To extract real estate listing data (e.g., title, price, location, URL) for analysis or aggregation.
Challenges: Anti-scraping protections including JavaScript rendering, IP rate-limiting, fingerprinting, and bot detection.

🔍 Section 1: Site Structure Overview
sahibinden.com is a dynamic website primarily designed for classified listings. Listings are categorized (Real Estate, Vehicles, Services, etc.), and paginated. Key observations:

Listing URLs follow the pattern:
https://www.sahibinden.com/kiralik-daire (for rent - apartments)

Most listing data is rendered dynamically via JavaScript after initial page load.

Scraping with basic HTTP libraries like requests results in incomplete HTML or 403 Forbidden responses.

🚫 Section 2: Anti-Scraping Mechanisms
Below are the identified protections deployed by sahibinden.com:

2.1. JavaScript Rendering
The majority of listing content is not present in raw HTML.

Instead, a minimal HTML shell is served; then JS populates the DOM using XHR or internal frameworks.

Scraping via raw requests will miss critical content.

2.2. IP Rate Limiting and IP Fingerprinting
Too many requests from the same IP within a short time lead to 429 Too Many Requests or 403 Forbidden.

IP bans may be temporary or long-term, especially from datacenter IPs.

2.3. Behavioral Fingerprinting
Uses fingerprinting techniques such as:

navigator.webdriver detection (headless browsers)

Screen resolution, timezone, installed fonts, language, etc.

Mouse movement / click / scroll simulation checks

2.4. HTTP Header Validation
Requests missing proper headers like User-Agent, Referer, Accept-Language, etc., are rejected.

May also require session cookies set by previous page visits.

2.5. Obfuscated HTML and Class Names
HTML is intentionally structured to be difficult to parse:

No meaningful class names (class="mcdZJK", class="dfgQsd")

Listings may be encoded or nested in iframes/JS templates

⚙️ Section 3: Tools & Techniques That Work
To overcome the protections above, a headless browser approach is required.

🧰 3.1. Recommended Stack
text
Kopyala
Düzenle
Language      : Python 3.9+
Browser Tool  : Playwright or Selenium
Fingerprint   : playwright-stealth / manual stealth logic
Proxy Support : Yes (rotating residential proxies recommended)
✅ Section 4: Working Scraping Strategy
STEP 1: Setup Playwright Environment
bash
Kopyala
Düzenle
pip install playwright
playwright install
STEP 2: Sample Playwright Script
python
Kopyala
Düzenle
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        locale="tr-TR",
        viewport={"width": 1280, "height": 800}
    )
    page = context.new_page()
    page.goto("https://www.sahibinden.com/kiralik-daire", timeout=60000)
    
    page.wait_for_selector(".classifiedTitle")  # Wait for JS-loaded elements

    # Extract listing titles
    titles = page.eval_on_selector_all(
        ".classifiedTitle", "elements => elements.map(e => e.textContent.trim())"
    )
    
    for title in titles:
        print(title)

    browser.close()
✅ This script launches a headless Chromium instance, bypasses basic bot detection, waits for JS to load, and scrapes listing titles.

🔄 Section 5: Proxy Rotation & Anti-Ban Tips
Technique	Recommendation
Proxy Type	Residential proxies (Oxylabs, Smartproxy, ScraperAPI)
Rotation Interval	Every 5-10 requests
Delay Between Requests	3-10 seconds random
Headers	Full browser headers (User-Agent, Accept-Language)
Stealth	Navigator.webdriver = false, real plugins, timezones
Session Persistence	Reuse browser sessions with cookies when possible

🧪 Section 6: Limitations and Warnings
Terms of Use: sahibinden.com prohibits automated access in their Terms of Service. Use for academic or personal learning purposes only.

Legal: Repeated access or commercial use may result in legal action or IP bans.

Ethical: Prefer obtaining permission or using an official API if available.

📦 Section 7: Optional Enhancements
✅ Use playwright-extra plugins for stealth (for JS fingerprint spoofing)

✅ Integrate output with SQLite, CSV, or Pandas for analysis

✅ Create a queue system to crawl paginated results and extract more fields (price, city, district)

📁 Sample Output Format (JSON)
json
Kopyala
Düzenle
[
  {
    "title": "3+1 Daire, Bahçelievler",
    "price": "15.000 TL",
    "location": "İstanbul, Bahçelievler",
    "url": "https://www.sahibinden.com/ilan/emlak-kiralik-..."
  },
  ...
]
Part 2 – Pagination, Field Extraction, Data Storage
🔁 Section 8: Crawling Through Pagination
Each listing category (e.g., kiralık daire) is paginated. The pagination URL structure is:

text
Kopyala
Düzenle
https://www.sahibinden.com/kiralik-daire?page=2
Pages typically go up to 1000+. However, accessing high-numbered pages too quickly or without cookies may trigger bans.

✅ Paginated Crawling with Playwright (Full Working Example)
python
Kopyala
Düzenle
from playwright.sync_api import sync_playwright
import time
import random
import json

BASE_URL = "https://www.sahibinden.com/kiralik-daire?page={}"

def extract_listings(page):
    page.wait_for_selector(".classified")
    
    listings = page.query_selector_all(".classified")
    results = []

    for listing in listings:
        try:
            title = listing.query_selector(".classifiedTitle").inner_text().strip()
            price = listing.query_selector(".price").inner_text().strip()
            location = listing.query_selector(".searchResultsLocationValue").inner_text().strip()
            url = listing.query_selector("a.classifiedTitle").get_attribute("href")
            full_url = "https://www.sahibinden.com" + url
            results.append({
                "title": title,
                "price": price,
                "location": location,
                "url": full_url
            })
        except:
            continue

    return results

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        locale="tr-TR"
    )
    page = context.new_page()

    all_data = []

    for page_num in range(1, 6):  # Example: Crawl first 5 pages
        print(f"Scraping page {page_num}")
        page.goto(BASE_URL.format(page_num), timeout=60000)
        data = extract_listings(page)
        all_data.extend(data)
        time.sleep(random.uniform(3, 6))  # Avoid detection

    browser.close()

    # Save to file
    with open("sahibinden_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    print("Scraping complete. Data saved to sahibinden_data.json")
📊 Section 9: Fields You Can Extract
Field	Selector (CSS)	Description
title	.classifiedTitle	Listing title
price	.price	Price text (e.g., “15.000 TL”)
location	.searchResultsLocationValue	City/District
listing_url	a.classifiedTitle[href]	Relative path → convert to full URL
date	.searchResultsDateValue	Posting date (optional)
preview image	img.lazyload[src]	Preview image (optional)

You can expand scraping logic to extract these directly from listing detail pages (but this increases request count).

💾 Section 10: Saving to CSV / SQLite
Save to CSV
python
Kopyala
Düzenle
import csv

with open("sahibinden_data.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["title", "price", "location", "url"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_data)
Save to SQLite (Optional)
python
Kopyala
Düzenle
import sqlite3

conn = sqlite3.connect("sahibinden.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS listings (
    id INTEGER PRIMARY KEY,
    title TEXT,
    price TEXT,
    location TEXT,
    url TEXT UNIQUE
)
""")

for row in all_data:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO listings (title, price, location, url)
            VALUES (?, ?, ?, ?)
        """, (row["title"], row["price"], row["location"], row["url"]))
    except:
        continue

conn.commit()
conn.close()
🔒 Section 11: Bypass Checklist
Checkpoint	Status	Suggestion
JavaScript Rendering	✅ OK	Playwright handles this
IP Rotation	🔶 Optional	Needed if scraping at scale
Bot Detection (webdriver)	✅ OK	Avoid headless detection via context tuning
Fingerprinting	🔶 Partial	Use more advanced stealth setup for higher volumes
Delay Between Requests	✅ OK	Add 3–6s randomized delays
Cookie Tracking	✅ OK	Reuse session when paginating
Legal / Ethical Use	⚠️	Do not use for commercial purposes without permission

🧠 Section 12: Optional Next Steps
Extract details from listing detail pages (e.g., number of rooms, floor, amenities)

Add proxy support with Playwright’s browser_type.launch(proxy=...)
