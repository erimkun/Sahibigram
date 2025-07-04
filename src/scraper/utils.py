"""
🛠️ Utility functions for sahibinden.com scraping
URL encoding, data validation, and helper functions
"""

import urllib.parse
import re
from typing import Dict, Any, Optional


class URLBuilder:
    """
    URL builder with Turkish character support
    Based on urlencoder.org findings and roadmap requirements
    """
    
    BASE_URL = "https://www.sahibinden.com"
    
    CATEGORY_MAP = {
        'kiralik_daire': 'kiralik-daire',
        'satilik_daire': 'satilik-daire',
        'kiralik_villa': 'kiralik-villa',
        'satilik_villa': 'satilik-villa',
        'kiralik_isyeri': 'kiralik-isyeri',
        'satilik_isyeri': 'satilik-isyeri'
    }
    
    def encode_turkish_location(self, location: str) -> str:
        """
        Encode Turkish characters in location names
        Using urlencoder.org compatible encoding
        
        Examples:
        İstanbul → %C4%B0stanbul
        Kadıköy → Kadik%C3%B6y
        Göztepe → G%C3%B6ztepe
        """
        if not location:
            return ""
        
        # Convert to lowercase for URL compatibility
        location = location.lower()
        
        # URL encode Turkish characters
        encoded = urllib.parse.quote(location, safe='')
        return encoded
    
    def build_category_url(self, category: str, location: Optional[str] = None) -> str:
        """
        Build category URL with optional location
        
        Args:
            category: Category key (e.g., 'kiralik_daire')
            location: Location name (e.g., 'İstanbul')
            
        Returns:
            Full URL string
        """
        if category not in self.CATEGORY_MAP:
            raise ValueError(f"Unknown category: {category}")
        
        url = f"{self.BASE_URL}/{self.CATEGORY_MAP[category]}"
        
        if location:
            encoded_location = self.encode_turkish_location(location)
            url += f"/{encoded_location}"
        
        return url
    
    def build_paginated_url(
        self,
        category: str,
        page: int = 1,
        location: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build paginated URL with filters
        
        Args:
            category: Category key
            page: Page number
            location: Location filter
            filters: Additional filters
            
        Returns:
            Full URL with query parameters
        """
        base_url = self.build_category_url(category, location)
        
        # Build query parameters
        params = []
        
        # Add page parameter
        if page > 1:
            params.append(f"page={page}")
        
        # Add additional filters
        if filters:
            for key, value in filters.items():
                if value:
                    # Encode string values
                    if isinstance(value, str):
                        encoded_value = urllib.parse.quote(str(value), safe='')
                    else:
                        encoded_value = str(value)
                    params.append(f"{key}={encoded_value}")
        
        if params:
            return f"{base_url}?{'&'.join(params)}"
        
        return base_url
    
    def build_search_url(
        self,
        search_term: str,
        category: str = 'kiralik_daire',
        page: int = 1
    ) -> str:
        """
        Build search URL with search term
        
        Args:
            search_term: Search query
            category: Category to search in
            page: Page number
            
        Returns:
            Search URL
        """
        filters = {'query': search_term}
        return self.build_paginated_url(
            category=category,
            page=page,
            filters=filters
        )


class DataValidator:
    """
    Data validation for scraped listings
    """
    
    # Required fields for a valid listing
    REQUIRED_FIELDS = ['title', 'price', 'location']
    
    # Price patterns to validate
    PRICE_PATTERNS = [
        r'\d+\.?\d*\s*TL',  # Turkish Lira
        r'\d+\.?\d*\s*₺',   # Turkish Lira symbol
        r'\d+\.?\d*\s*EUR', # Euro
        r'\d+\.?\d*\s*USD', # US Dollar
    ]
    
    def is_valid_listing(self, listing_data: Dict[str, Any]) -> bool:
        """
        Validate if listing data is complete and valid
        
        Args:
            listing_data: Dictionary containing listing information
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(listing_data, dict):
            return False
        
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in listing_data or not listing_data[field]:
                return False
        
        # Validate price format
        if not self.is_valid_price(listing_data['price']):
            return False
        
        # Validate URL if present
        if 'url' in listing_data and listing_data['url']:
            if not self.is_valid_url(listing_data['url']):
                return False
        
        return True
    
    def is_valid_price(self, price: str) -> bool:
        """
        Validate price format
        
        Args:
            price: Price string
            
        Returns:
            True if valid price format
        """
        if not price or not isinstance(price, str):
            return False
        
        # Check against price patterns
        for pattern in self.PRICE_PATTERNS:
            if re.search(pattern, price, re.IGNORECASE):
                return True
        
        return False
    
    def is_valid_url(self, url: str) -> bool:
        """
        Validate URL format
        
        Args:
            url: URL string
            
        Returns:
            True if valid URL
        """
        if not url or not isinstance(url, str):
            return False
        
        # Basic URL validation
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(url_pattern, url))
    
    def clean_price(self, price: str) -> str:
        """
        Clean and normalize price string
        
        Args:
            price: Raw price string
            
        Returns:
            Cleaned price string
        """
        if not price:
            return ""
        
        # Remove extra whitespace
        price = price.strip()
        
        # Normalize currency symbols
        price = price.replace('₺', 'TL')
        
        # Remove multiple spaces
        price = re.sub(r'\s+', ' ', price)
        
        return price
    
    def clean_location(self, location: str) -> str:
        """
        Clean and normalize location string
        
        Args:
            location: Raw location string
            
        Returns:
            Cleaned location string
        """
        if not location:
            return ""
        
        # Remove extra whitespace
        location = location.strip()
        
        # Capitalize first letter of each word
        location = location.title()
        
        return location


class DataProcessor:
    """
    Post-processing utilities for scraped data
    """
    
    def __init__(self):
        self.validator = DataValidator()
    
    def process_listings(self, raw_listings: list) -> list:
        """
        Process and clean raw listings data
        
        Args:
            raw_listings: List of raw listing dictionaries
            
        Returns:
            List of processed and validated listings
        """
        processed_listings = []
        
        for listing in raw_listings:
            try:
                # Clean individual fields
                if 'price' in listing:
                    listing['price'] = self.validator.clean_price(listing['price'])
                
                if 'location' in listing:
                    listing['location'] = self.validator.clean_location(listing['location'])
                
                # Validate processed listing
                if self.validator.is_valid_listing(listing):
                    processed_listings.append(listing)
                
            except Exception as e:
                print(f"Error processing listing: {e}")
                continue
        
        return processed_listings
    
    def remove_duplicates(self, listings: list) -> list:
        """
        Remove duplicate listings based on URL
        
        Args:
            listings: List of listings
            
        Returns:
            List with duplicates removed
        """
        seen_urls = set()
        unique_listings = []
        
        for listing in listings:
            url = listing.get('url')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_listings.append(listing)
            elif not url:
                # Keep listings without URLs
                unique_listings.append(listing)
        
        return unique_listings
    
    def filter_by_price_range(
        self,
        listings: list,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None
    ) -> list:
        """
        Filter listings by price range
        
        Args:
            listings: List of listings
            min_price: Minimum price (optional)
            max_price: Maximum price (optional)
            
        Returns:
            Filtered listings
        """
        filtered_listings = []
        
        for listing in listings:
            price_str = listing.get('price', '')
            
            # Extract numeric price
            price_numbers = re.findall(r'[\d.]+', price_str.replace(',', '.'))
            
            if price_numbers:
                try:
                    price = float(price_numbers[0])
                    
                    # Check price range
                    if min_price is not None and price < min_price:
                        continue
                    if max_price is not None and price > max_price:
                        continue
                    
                    filtered_listings.append(listing)
                    
                except ValueError:
                    # Skip if price conversion fails
                    continue
        
        return filtered_listings 