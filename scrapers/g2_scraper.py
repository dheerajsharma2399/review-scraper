"""
G2 Reviews Scraper
Scrapes reviews from G2.com for a given company and date range.
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

def setup_driver(no_headless=False):
    """Set up Chrome driver with options to mimic real browser."""
    options = Options()
    if not no_headless:
        options.add_argument("--headless")  # Run in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.binary_location = "C:\\chrome-win64\\chrome.exe"
    
    service = Service(executable_path="E:\\Assignment_data\\review scraper\\drivers\\chromedriver-win64\\chromedriver.exe")
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_g2_reviews(company, start_date, end_date, no_headless=False):
    """Scrape G2 reviews for the company within date range."""
    slug = company.lower().replace(" ", "-")
    url = f"https://www.g2.com/products/{slug}/reviews"
    
    driver = setup_driver(no_headless=no_headless)
    reviews = []
    
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        # Wait for reviews to load
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".oc-product-review-card")))  # G2 review card
        # Scroll to load more if lazy-loaded
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        
        while True:
            # Extract reviews from current page
            review_elements = driver.find_elements(By.CSS_SELECTOR, ".oc-product-review-card")  # G2 review cards
            for elem in review_elements:
                try:
                    title = elem.find_element(By.CSS_SELECTOR, ".pros-cons-review__title-text").text  # G2 title
                    description = elem.find_element(By.CSS_SELECTOR, ".pros-cons-review__body").text  # G2 description
                    date_str = elem.find_element(By.CSS_SELECTOR, '[data-testid="review-date"] .text').text  # G2 date
                    # Parse date to YYYY-MM-DD if needed
                    date = parse_date(date_str)  # Implement parse_date
                    rating = elem.find_element(By.CSS_SELECTOR, ".review-rating .count").text  # G2 rating
                    reviewer = elem.find_element(By.CSS_SELECTOR, ".reviewer-name").text  # G2 reviewer
                    
                    review = {
                        "title": title,
                        "description": description,
                        "date": date,  # Now YYYY-MM-DD str
                        "rating": rating,
                        "reviewer_name": reviewer
                    }
                    
                    reviews.append(review)
                except Exception as e:
                    print(f"Error extracting review: {e}")
                    continue
            
            # Pagination: Check for next button
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".next-page-button")  # G2 pagination
                if "disabled" in next_button.get_attribute("class"):
                    break
                next_button.click()
                time.sleep(2)  # Delay to avoid detection
            except:
                break
        
    except Exception as e:
        print(f"Error scraping G2: {e}")
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
        # Fallback for unparseable dates
        return None  # Skip in main filter if None