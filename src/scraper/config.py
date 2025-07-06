"""
⚙️ Configuration management for sahibinden.com scraper
Centralized settings based on proven working parameters
"""

import os
from typing import Dict, Any


class ScraperConfig:
    """
    Configuration class for SahibindenScraper
    Based on proven working settings from AdditionalReport.md
    """
    
    # Base URLs and endpoints
    BASE_URL = "https://www.sahibinden.com"
    
    # Browser configuration (PROVEN WORKING)
    HEADLESS = True
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    LOCALE = "tr-TR"
    VIEWPORT = {"width": 1280, "height": 800}
    TIMEZONE = "Europe/Istanbul"
    
    # Timing configuration (ANTI-DETECTION)
    MIN_DELAY = 3.0  # Minimum delay between requests (seconds)
    MAX_DELAY = 6.0  # Maximum delay between requests (seconds)
    PAGE_TIMEOUT = 60000  # Page load timeout (milliseconds)
    
    # Optional proxy (e.g. http://user:pass@proxy.example.com:8000)
    PROXY_SERVER: str | None = None
    
    # Scraping limits
    DEFAULT_MAX_PAGES = 5
    MAX_RETRIES = 3
    
    # CSS Selectors (PROVEN WORKING)
    SELECTORS = {
        'listing_container': 'tr.searchResultsItem',
        'title': '.classifiedTitle',
        'price': '.searchResultsPriceValue',
        'location': '.searchResultsLocationValue',
        'date': '.searchResultsDateValue',
        'url': 'a.classifiedTitle',
        'image': 'img.lazyload'
    }
    
    # Export settings
    DEFAULT_EXPORT_FORMAT = 'json'
    EXPORT_DIRECTORY = 'exports'
    
    # Logging configuration
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Data validation settings
    REQUIRED_FIELDS = ['title', 'price', 'location']
    
    # Categories mapping
    CATEGORIES = {
        'kiralik_daire': 'kiralik-daire',
        'satilik_daire': 'satilik-daire',
        'kiralik_villa': 'kiralik-villa',
        'satilik_villa': 'satilik-villa',
        'kiralik_isyeri': 'kiralik-isyeri',
        'satilik_isyeri': 'satilik-isyeri'
    }
    
    def __init__(self, **kwargs):
        """
        Initialize configuration with optional overrides
        
        Args:
            **kwargs: Configuration overrides
        """
        # Apply any provided overrides
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Load environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # Browser settings
        self.HEADLESS = os.getenv('SAHIBI_HEADLESS', str(self.HEADLESS)).lower() == 'true'
        self.USER_AGENT = os.getenv('SAHIBI_USER_AGENT', self.USER_AGENT)
        
        # Timing settings
        self.MIN_DELAY = float(os.getenv('SAHIBI_MIN_DELAY', self.MIN_DELAY))
        self.MAX_DELAY = float(os.getenv('SAHIBI_MAX_DELAY', self.MAX_DELAY))
        self.PAGE_TIMEOUT = int(os.getenv('SAHIBI_PAGE_TIMEOUT', self.PAGE_TIMEOUT))
        
        # Scraping limits
        self.DEFAULT_MAX_PAGES = int(os.getenv('SAHIBI_MAX_PAGES', self.DEFAULT_MAX_PAGES))
        
        # Export settings
        self.EXPORT_DIRECTORY = os.getenv('SAHIBI_EXPORT_DIR', self.EXPORT_DIRECTORY)
        
        # Logging
        self.LOG_LEVEL = os.getenv('SAHIBI_LOG_LEVEL', self.LOG_LEVEL)
        
        # Proxy
        self.PROXY_SERVER = os.getenv('SAHIBI_PROXY', self.PROXY_SERVER)
    
    def get_browser_args(self) -> list:
        """Get browser launch arguments"""
        return [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-accelerated-2d-canvas',
            '--disable-gpu',
            '--window-size=1920,1080',
            '--disable-blink-features=AutomationControlled',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images'  # Faster loading
        ]
    
    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for requests"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'User-Agent': self.USER_AGENT
        }
    
    def get_context_options(self) -> Dict[str, Any]:
        """Get browser context options"""
        return {
            'user_agent': self.USER_AGENT,
            'locale': self.LOCALE,
            'viewport': self.VIEWPORT,
            'timezone_id': self.TIMEZONE,
            'java_script_enabled': True,
            'accept_downloads': False,
            'bypass_csp': True,
            'ignore_https_errors': True
        }
    
    def get_proxy(self) -> Dict[str, str] | None:
        """Return Playwright proxy dict if proxy is configured."""
        if self.PROXY_SERVER:
            return {"server": self.PROXY_SERVER}
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'base_url': self.BASE_URL,
            'headless': self.HEADLESS,
            'user_agent': self.USER_AGENT,
            'locale': self.LOCALE,
            'viewport': self.VIEWPORT,
            'timezone': self.TIMEZONE,
            'min_delay': self.MIN_DELAY,
            'max_delay': self.MAX_DELAY,
            'page_timeout': self.PAGE_TIMEOUT,
            'default_max_pages': self.DEFAULT_MAX_PAGES,
            'max_retries': self.MAX_RETRIES,
            'export_directory': self.EXPORT_DIRECTORY,
            'log_level': self.LOG_LEVEL
        }
    
    def __str__(self) -> str:
        """String representation of configuration"""
        return f"ScraperConfig(headless={self.HEADLESS}, max_pages={self.DEFAULT_MAX_PAGES})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return f"ScraperConfig({self.to_dict()})"


# Predefined configurations for different use cases
class DevelopmentConfig(ScraperConfig):
    """Configuration for development environment"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.HEADLESS = False  # Show browser for debugging
        self.MIN_DELAY = 5.0   # Slower for debugging
        self.MAX_DELAY = 10.0
        self.DEFAULT_MAX_PAGES = 2  # Limit pages for testing
        self.LOG_LEVEL = 'DEBUG'


class ProductionConfig(ScraperConfig):
    """Configuration for production environment"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.HEADLESS = True
        self.MIN_DELAY = 2.0   # Faster for production
        self.MAX_DELAY = 4.0
        self.DEFAULT_MAX_PAGES = 50  # More pages for production
        self.LOG_LEVEL = 'INFO'


class FastConfig(ScraperConfig):
    """Configuration for fast scraping (higher risk of detection)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.HEADLESS = True
        self.MIN_DELAY = 1.0   # Faster but riskier
        self.MAX_DELAY = 2.0
        self.DEFAULT_MAX_PAGES = 10
        self.LOG_LEVEL = 'WARNING'


class SafeConfig(ScraperConfig):
    """Configuration for safe scraping (lower risk of detection)"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.HEADLESS = True
        self.MIN_DELAY = 8.0   # Slower but safer
        self.MAX_DELAY = 15.0
        self.DEFAULT_MAX_PAGES = 5
        self.LOG_LEVEL = 'INFO'


# Configuration factory
def get_config(config_type: str = 'default', **kwargs) -> ScraperConfig:
    """
    Factory function to get configuration instances
    
    Args:
        config_type: Type of configuration ('default', 'development', 'production', 'fast', 'safe')
        **kwargs: Additional configuration overrides
        
    Returns:
        ScraperConfig instance
    """
    config_map = {
        'default': ScraperConfig,
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'fast': FastConfig,
        'safe': SafeConfig
    }
    
    if config_type not in config_map:
        raise ValueError(f"Unknown config type: {config_type}")
    
    return config_map[config_type](**kwargs) 