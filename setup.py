#!/usr/bin/env python3
"""
🚀 Setup script for Sahibigram - sahibinden.com Scraper
Quick installation and environment setup
"""

import os
import sys
import subprocess
import platform


def run_command(command, description=""):
    """Run a command and handle errors"""
    print(f"🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_playwright():
    """Install Playwright and browsers"""
    print("🎭 Installing Playwright...")
    
    # Install Playwright
    if not run_command("pip install playwright", "Installing Playwright package"):
        return False
    
    # Install browsers
    if not run_command("playwright install", "Installing Playwright browsers"):
        return False
    
    # Install system dependencies (Linux/Mac)
    if platform.system() != "Windows":
        run_command("playwright install-deps", "Installing system dependencies")
    
    return True


def install_requirements():
    """Install Python requirements"""
    print("📦 Installing Python requirements...")
    
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found")
        return False
    
    return run_command("pip install -r requirements.txt", "Installing requirements")


def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    
    directories = [
        "exports",
        "logs",
        "data",
        "config"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   Created: {directory}/")
    
    return True


def create_env_file():
    """Create sample .env file"""
    print("⚙️ Creating sample .env file...")
    
    env_content = """# 🚀 Sahibigram Environment Configuration
# Copy this file to .env and modify as needed

# Scraper Configuration
SAHIBI_HEADLESS=true
SAHIBI_MIN_DELAY=3
SAHIBI_MAX_DELAY=6
SAHIBI_MAX_PAGES=5
SAHIBI_LOG_LEVEL=INFO
SAHIBI_EXPORT_DIR=exports

# Browser Configuration
SAHIBI_USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
SAHIBI_PAGE_TIMEOUT=60000

# Development Mode (set to false for production)
DEVELOPMENT_MODE=true
"""
    
    with open(".env.example", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ Sample .env file created as .env.example")
    print("   Copy it to .env and modify as needed")
    return True


def run_test():
    """Run a simple test to verify installation"""
    print("🧪 Running installation test...")
    
    test_script = """
import sys
sys.path.insert(0, 'src')

try:
    from scraper.sahibinden_scraper import SahibindenScraper
    from scraper.utils import URLBuilder, DataValidator
    from scraper.config import get_config
    
    # Test imports
    scraper = SahibindenScraper()
    url_builder = URLBuilder()
    validator = DataValidator()
    config = get_config('development')
    
    # Test URL building
    test_url = url_builder.build_category_url('kiralik_daire', 'İstanbul')
    
    # Test data validation
    test_data = {'title': 'Test', 'price': '1000 TL', 'location': 'İstanbul'}
    is_valid = validator.is_valid_listing(test_data)
    
    print("✅ All imports successful")
    print(f"✅ URL building works: {test_url}")
    print(f"✅ Data validation works: {is_valid}")
    
except Exception as e:
    print(f"❌ Test failed: {str(e)}")
    sys.exit(1)
"""
    
    with open("test_installation.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    success = run_command("python test_installation.py", "Running installation test")
    
    # Clean up test file
    if os.path.exists("test_installation.py"):
        os.remove("test_installation.py")
    
    return success


def main():
    """Main setup function"""
    print("🚀 Sahibigram Setup - sahibinden.com Scraper")
    print("=" * 60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing Python requirements", install_requirements),
        ("Installing Playwright", install_playwright),
        ("Creating directories", create_directories),
        ("Creating environment file", create_env_file),
        ("Running installation test", run_test)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        print("-" * 40)
        
        if not step_func():
            failed_steps.append(step_name)
            print(f"❌ Step '{step_name}' failed")
        else:
            print(f"✅ Step '{step_name}' completed")
    
    print("\n" + "=" * 60)
    
    if failed_steps:
        print("❌ Setup completed with errors:")
        for step in failed_steps:
            print(f"   - {step}")
        print("\n🔧 Please fix the errors above and run setup again")
        return False
    
    print("✅ Setup completed successfully!")
    print("\n🎉 Your scraper is ready to use!")
    print("\n📖 Next steps:")
    print("   1. Run: python example_basic.py")
    print("   2. Check the exports/ directory for results")
    print("   3. Review the logs/ directory for debug info")
    print("   4. Modify .env file for custom configuration")
    
    return True


if __name__ == "__main__":
    success = main()
    
    if not success:
        sys.exit(1)
    
    print("\n🚀 Ready to scrape sahibinden.com!") 