"""
🏠 SahibindenScraper - Main scraper class for sahibinden.com
Based on the proven working solution from AdditionalReport.md
"""

import time
import random
import json
import logging
from typing import List, Dict, Optional, Any
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin


class SahibindenScraper:
    """
    Production-ready sahibinden.com scraper
    Based on proven Playwright solution with anti-detection measures
    """
    
    def __init__(self):
        """Initialize the scraper"""
        self.BASE_URL = "https://www.sahibinden.com"
        self.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.LOCALE = "tr-TR"
        self.VIEWPORT = {"width": 1280, "height": 800}
        self.MIN_DELAY = 3
        self.MAX_DELAY = 6
        self.PAGE_TIMEOUT = 60000
        
        # Setup logging
        self.logger = logging.getLogger('SahibindenScraper')
        self.logger.setLevel(logging.INFO)
        
        # Playwright instances
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Statistics
        self.stats = {
            'total_pages_scraped': 0,
            'total_listings_found': 0,
            'successful_extractions': 0,
            'failed_extractions': 0
        }
    
    def start_browser(self):
        """Start Playwright browser with anti-detection configuration"""
        try:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.context = self.browser.new_context(
                user_agent=self.USER_AGENT,
                locale=self.LOCALE,
                viewport=self.VIEWPORT
            )
            self.page = self.context.new_page()
            self.logger.info("Browser started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start browser: {str(e)}")
            raise
    
    def stop_browser(self):
        """Clean up browser instances"""
        try:
            if self.page:
                self.page.close()
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
            self.logger.info("Browser stopped successfully")
        except Exception as e:
            self.logger.error(f"Error stopping browser: {str(e)}")
    
    def _random_delay(self):
        """Add random delay to avoid detection"""
        delay = random.uniform(self.MIN_DELAY, self.MAX_DELAY)
        time.sleep(delay)
    
    def _extract_listings_from_page(self, page):
        """Extract listings from current page using proven selectors"""
        try:
            # Wait for listings to load
            page.wait_for_selector(".classified", timeout=self.PAGE_TIMEOUT)
            
            # Get all listing elements
            listings = page.query_selector_all(".classified")
            results = []
            
            for listing in listings:
                try:
                    # Extract data using proven selectors from AdditionalReport.md
                    title_element = listing.query_selector(".classifiedTitle")
                    price_element = listing.query_selector(".price")
                    location_element = listing.query_selector(".searchResultsLocationValue")
                    date_element = listing.query_selector(".searchResultsDateValue")
                    url_element = listing.query_selector("a.classifiedTitle")
                    image_element = listing.query_selector(".lazyload")
                    
                    # Extract text content
                    title = title_element.inner_text().strip() if title_element else None
                    price = price_element.inner_text().strip() if price_element else None
                    location = location_element.inner_text().strip() if location_element else None
                    date = date_element.inner_text().strip() if date_element else None
                    
                    # Extract URL and image
                    relative_url = url_element.get_attribute("href") if url_element else None
                    full_url = urljoin(self.BASE_URL, relative_url) if relative_url else None
                    image_url = image_element.get_attribute("src") if image_element else None
                    
                    # Create listing data
                    listing_data = {
                        'title': title,
                        'price': price,
                        'location': location,
                        'date': date,
                        'url': full_url,
                        'image_url': image_url,
                        'scraped_at': time.time()
                    }
                    
                    # Only add if we have essential data
                    if title and price and location:
                        results.append(listing_data)
                        self.stats['successful_extractions'] += 1
                    else:
                        self.stats['failed_extractions'] += 1
                        
                except Exception as e:
                    self.logger.error(f"Error extracting listing: {str(e)}")
                    self.stats['failed_extractions'] += 1
                    continue
            
            self.logger.info(f"Extracted {len(results)} listings from page")
            return results
            
        except Exception as e:
            self.logger.error(f"Error extracting listings from page: {str(e)}")
            return []
    
    def scrape_pages(self, base_url, max_pages=5):
        """
        Scrape multiple pages - Core functionality from AdditionalReport.md
        """
        if not self.browser:
            self.start_browser()
        
        all_listings = []
        
        try:
            for page_num in range(1, max_pages + 1):
                self.logger.info(f"Scraping page {page_num}/{max_pages}")
                
                # Build URL for current page
                url = f"{base_url}?page={page_num}"
                
                # Navigate to page
                self.page.goto(url, timeout=self.PAGE_TIMEOUT)
                
                # Extract listings
                page_listings = self._extract_listings_from_page(self.page)
                all_listings.extend(page_listings)
                
                # Update statistics
                self.stats['total_pages_scraped'] += 1
                self.stats['total_listings_found'] += len(page_listings)
                
                # Random delay to avoid detection
                self._random_delay()
                
                # Break if no listings found
                if not page_listings:
                    self.logger.info(f"No more listings found at page {page_num}")
                    break
            
            self.logger.info(f"Scraping completed. Total listings: {len(all_listings)}")
            return all_listings
            
        except Exception as e:
            self.logger.error(f"Error during scraping: {str(e)}")
            return all_listings
    
    def export_data(self, data, filename, format='json'):
        """Export scraped data to file"""
        try:
            if format == 'json':
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            elif format == 'csv':
                import csv
                if data:
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=data[0].keys())
                        writer.writeheader()
                        writer.writerows(data)
            
            self.logger.info(f"Data exported to {filename} ({format})")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting data: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop_browser() 