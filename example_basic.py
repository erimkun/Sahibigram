#!/usr/bin/env python3
"""
🏠 Basic Example - sahibinden.com Scraper
Demo script showing how to use the scraper based on working solution
"""

import os
import sys
import logging
from datetime import datetime
from pathlib import Path

# Add src to path for imports
ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from scraper.sahibinden_scraper import SahibindenScraper  # type: ignore
from scraper.utils import URLBuilder, DataProcessor  # type: ignore
from scraper.config import get_config  # type: ignore


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('scraper.log')
        ]
    )


def main():
    """
    Main function demonstrating scraper usage
    Based on working solution from AdditionalReport.md
    """
    print("🚀 Sahibigram - sahibinden.com Scraper")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Create export directory
    os.makedirs('exports', exist_ok=True)
    
    try:
        # Initialize scraper (based on working solution)
        logger.info("Initializing scraper...")
        scraper = SahibindenScraper()
        
        # Initialize URL builder and data processor
        url_builder = URLBuilder()
        data_processor = DataProcessor()
        
        # Build URL for kiralık daire (rental apartments)
        # This is the exact URL pattern from AdditionalReport.md
        base_url = "https://www.sahibinden.com/kiralik-daire"
        
        print(f"📍 Target URL: {base_url}")
        print(f"📄 Max Pages: 5")
        print(f"⏱️ Starting scraping...")
        
        # Start scraping using the proven method
        with scraper:
            logger.info("Starting scraping process...")
            
            # Scrape pages using the working solution approach
            listings = scraper.scrape_pages(
                base_url=base_url,
                max_pages=5
            )
            
            logger.info(f"Scraped {len(listings)} listings")
            
            # Process the scraped data
            logger.info("Processing scraped data...")
            processed_listings = data_processor.process_listings(listings)
            
            # Remove duplicates
            unique_listings = data_processor.remove_duplicates(processed_listings)
            
            logger.info(f"Processed {len(unique_listings)} unique listings")
            
            # Display sample results
            print("\n📊 Scraping Results:")
            print(f"   Total listings found: {len(listings)}")
            print(f"   Unique listings: {len(unique_listings)}")
            print(f"   Success rate: {scraper.stats['successful_extractions']}/{scraper.stats['successful_extractions'] + scraper.stats['failed_extractions']}")
            
            # Show sample listings
            print("\n🏠 Sample Listings:")
            for i, listing in enumerate(unique_listings[:3]):
                print(f"\n   {i+1}. {listing['title']}")
                print(f"      Price: {listing['price']}")
                print(f"      Location: {listing['location']}")
                print(f"      URL: {listing['url'][:80]}...")
            
            # Export data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Export to JSON
            json_filename = f"exports/sahibinden_listings_{timestamp}.json"
            scraper.export_data(unique_listings, json_filename, 'json')
            
            # Export to CSV
            csv_filename = f"exports/sahibinden_listings_{timestamp}.csv"
            scraper.export_data(unique_listings, csv_filename, 'csv')
            
            print(f"\n💾 Data exported to:")
            print(f"   📄 JSON: {json_filename}")
            print(f"   📊 CSV: {csv_filename}")
            
            # Show statistics
            print(f"\n📈 Statistics:")
            print(f"   Pages scraped: {scraper.stats['total_pages_scraped']}")
            print(f"   Total listings found: {scraper.stats['total_listings_found']}")
            print(f"   Successful extractions: {scraper.stats['successful_extractions']}")
            print(f"   Failed extractions: {scraper.stats['failed_extractions']}")
            
    except Exception as e:
        logger.error(f"Error during scraping: {str(e)}")
        print(f"❌ Error: {str(e)}")
        return False
    
    print("\n✅ Scraping completed successfully!")
    return True


def demo_url_builder():
    """Demonstrate URL building with Turkish characters"""
    print("\n🔧 URL Builder Demo:")
    print("=" * 30)
    
    url_builder = URLBuilder()
    
    # Test Turkish character encoding
    test_locations = [
        "İstanbul",
        "Kadıköy", 
        "Göztepe",
        "Şişli",
        "Çankaya"
    ]
    
    for location in test_locations:
        encoded_url = url_builder.build_category_url('kiralik_daire', location)
        print(f"   {location} → {encoded_url}")


def demo_configurations():
    """Demonstrate different configuration options"""
    print("\n⚙️ Configuration Demo:")
    print("=" * 30)
    
    configs = ['development', 'production', 'fast', 'safe']
    
    for config_type in configs:
        config = get_config(config_type)
        print(f"   {config_type.title()}: {config}")


if __name__ == "__main__":
    print("Starting sahibinden.com scraper demonstration...")
    
    # Run demos
    demo_url_builder()
    demo_configurations()
    
    # Run main scraping
    print("\n" + "=" * 50)
    success = main()
    
    if success:
        print("\n🎉 Demo completed successfully!")
    else:
        print("\n❌ Demo failed!")
        sys.exit(1) 