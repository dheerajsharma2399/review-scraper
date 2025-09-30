"""
TrustRadius Reviews Scraper
Scrapes reviews from TrustRadius.com for a given company and date range.
Note: Selectors may need adjustment based on site changes. Anti-bot measures may require proxies/headers.
Some content may require login; this is a basic implementation.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import time
from dateutil import parser as date_parser

def setup_driver():
    """Set up Chrome driver with options to mimic real browser."""
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_trustradius_reviews(company, start_date, end_date):
    """Scrape TrustRadius reviews for the company within date range."""
    slug = company.lower().replace(" ", "-")
    url = f"https://www.trustradius.com/products/{slug}/reviews"
    
    driver = setup_driver()
    reviews = []
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        # Wait for reviews to load
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "review-item")))  # TODO: Confirm selector
        
        while True:
            # Extract reviews from current page
            review_elements = driver.find_elements(By.CLASS_NAME, "review-item")  # TODO: Confirm
            for elem in review_elements:
                try:
                    title = elem.find_element(By.CSS_SELECTOR, ".review-title").text  # TODO: Confirm selector
                    description = elem.find_element(By.CSS_SELECTOR, ".review-content").text  # TODO: Confirm
                    date_str = elem.find_element(By.CSS_SELECTOR, ".review-date").text  # TODO: e.g., "2023-01-15"
                    date = parse_date(date_str)  # Implement parse_date
                    rating = elem.find_element(By.CSS_SELECTOR, ".rating-score").text  # TODO
                    reviewer = elem.find_element(By.CSS_SELECTOR, ".author-name").text  # TODO
                    
                    if date is None:
                        continue
                    
                    review = {
                        "title": title,
                        "description": description,
                        "date": date,
                        "rating": rating,
                        "reviewer_name": reviewer
                    }
                    
                    reviews.append(review)
                except Exception as e:
                    print(f"Error extracting review: {e}")
                    continue
            
            # Pagination: Check for next button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".next-button")  # TODO: Confirm
                if not next_button.is_enabled():
                    break
                next_button.click()
                time.sleep(2)  # Delay to avoid detection
            except:
                break
        
        # No post-filter; main.py handles it
        
    except Exception as e:
        print(f"Error scraping TrustRadius: {e}")
        reviews = []
    finally:
        driver.quit()
    
    return reviews

def parse_date(date_str):
    """Parse various date formats to YYYY-MM-DD."""
    try:
        parsed = date_parser.parse(date_str)
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return None  # Skip invalid dates