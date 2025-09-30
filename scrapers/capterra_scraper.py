"""
Capterra Reviews Scraper
Scrapes reviews from Capterra.com for a given company and date range.
Note: Selectors may need adjustment based on site changes. Anti-bot measures may require proxies/headers.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time
from dateutil import parser as date_parser
from urllib.parse import urlparse

def setup_driver():
    """Set up Chrome driver with options to mimic real browser."""
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('useAutomationExtension', False)
    options.binary_location = "C:\\chrome-win64\\chrome.exe"
    
    service = Service(executable_path="E:\\Assignment_data\\review scraper\\drivers\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def get_capterra_product_info(driver, company):
    """Search for company on Capterra and extract product ID and slug from first result."""
    search_url = f"https://www.capterra.com/search?type=products&query={company.replace(' ', '+')}"
    driver.get(search_url)
    wait = WebDriverWait(driver, 10)
    
    try:
        # Wait for search results
        first_result = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sl-search-result-card:first-of-type a[href^='/p/']")))
        href = first_result.get_attribute('href')
        parsed = urlparse(href)
        path_parts = parsed.path.split('/')
        if len(path_parts) >= 3 and path_parts[1] == 'p':
            product_id = path_parts[2]
            slug = '/'.join(path_parts[3:]) if len(path_parts) > 3 else ''
            return product_id, slug
    except Exception as e:
        print(f"Error finding product info for {company}: {e}")
    return None, None

def scrape_capterra_reviews(company, start_date, end_date):
    """Scrape Capterra reviews for the company within date range."""
    driver = setup_driver()
    reviews = []
    
    product_id, slug = get_capterra_product_info(driver, company)
    if not product_id:
        print(f"No product found for {company} on Capterra.")
        driver.quit()
        return []
    
    url = f"https://www.capterra.com/p/{product_id}/{slug}/reviews/"
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        # Wait for reviews to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sl-review-card")))  # Capterra review card
        
        while True:
            # Extract reviews from current page
            review_elements = driver.find_elements(By.CSS_SELECTOR, ".sl-review-card")  # Capterra review cards
            for elem in review_elements:
                try:
                    title = elem.find_element(By.CSS_SELECTOR, ".sl-review-card__title").text  # Capterra title
                    description = elem.find_element(By.CSS_SELECTOR, ".sl-review-card__body").text  # Capterra description
                    date_str = elem.find_element(By.CSS_SELECTOR, ".sl-review-card__date").text  # Capterra date
                    date = parse_date(date_str)  # YYYY-MM-DD str or None
                    rating = elem.find_element(By.CSS_SELECTOR, ".sl-rating__value").text  # Capterra rating
                    reviewer = elem.find_element(By.CSS_SELECTOR, ".sl-review-card__author-name").text  # Capterra reviewer
                    
                    if date is None:
                        continue  # Skip invalid dates
                    
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
                next_button = driver.find_element(By.CSS_SELECTOR, ".sl-pagination__next-button")  # Capterra pagination
                if not next_button.is_enabled():
                    break
                next_button.click()
                time.sleep(2)  # Delay to avoid detection
            except:
                break
        
        # No post-filter; main.py handles it
        
    except Exception as e:
        print(f"Error scraping Capterra: {e}")
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