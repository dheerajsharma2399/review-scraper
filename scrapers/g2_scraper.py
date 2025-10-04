import time
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from utils import date_utils, logger

class G2Scraper:
    def __init__(self, logger: logger.logging.Logger):
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.google.com/"
        })
        self.base_url = "https://www.g2.com"

    def _get_product_url(self, company: str) -> Optional[str]:
        """Search for the product and get its reviews URL."""
        search_url = f"{self.base_url}/search?query={company.replace(' ', '%20')}"
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            product_link = soup.find("a", {"data-testid": "product-card-link"})
            if product_link:
                product_url = self.base_url + product_link.get("href")
                # Append /reviews if not present
                if "/reviews" not in product_url:
                    product_url += "/reviews"
                self.logger.info(f"Found G2 product URL: {product_url}")
                return product_url
            else:
                self.logger.warning(f"No product found for {company} on G2")
                return None
        except requests.RequestException as e:
            self.logger.error(f"Error fetching G2 search: {e}")
            return None

    def _extract_review(self, review_elem: BeautifulSoup) -> Dict[str, Any]:
        """Extract review data from HTML element."""
        try:
            title_elem = review_elem.find("h3", class_="review-title")
            title = title_elem.get_text(strip=True) if title_elem else None

            body_elem = review_elem.find("div", class_="review-body")
            review_text = body_elem.get_text(strip=True) if body_elem else None

            date_elem = review_elem.find("span", class_="review-date")
            date_raw = date_elem.get_text(strip=True) if date_elem else None
            date = date_utils.parse_date(date_raw) if date_raw else None

            rating_elem = review_elem.find("div", {"data-testid": "review-rating"})
            rating = float(rating_elem.get("data-rating", 0)) if rating_elem else None

            reviewer_elem = review_elem.find("span", class_="reviewer-name")
            reviewer_name = reviewer_elem.get_text(strip=True) if reviewer_elem else None

            verified_elem = review_elem.find("span", string="Verified")
            verified = bool(verified_elem) if verified_elem else False

            helpful_elem = review_elem.find("span", class_="helpful-count")
            helpful_count = int(helpful_elem.get_text(strip=True)) if helpful_elem else 0

            return {
                "title": title,
                "review": review_text,
                "date": date,
                "date_raw": date_raw,
                "rating": rating,
                "reviewer_name": reviewer_name,
                "verified": verified,
                "helpful_count": helpful_count
            }
        except Exception as e:
            self.logger.error(f"Error extracting review: {e}")
            return {}

    def scrape(self, company: str, start_date: str, end_date: str, max_pages: int = 10) -> tuple[List[Dict[str, Any]], str]:
        """Scrape reviews from G2."""
        product_url = self._get_product_url(company)
        if not product_url:
            return [], ""

        all_reviews = []
        product_slug = company.lower().replace(" ", "-")
        page = 1
        while page <= max_pages:
            url = f"{product_url}?page={page}"
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 404:
                    self.logger.info(f"No more pages for {company} on G2")
                    break
                if response.status_code == 429:
                    self.logger.warning("Rate limited, waiting 60s")
                    time.sleep(60)
                    continue
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                review_elems = soup.find_all("div", class_="review-card")
                if not review_elems:
                    self.logger.info(f"No reviews found on page {page}")
                    break

                for elem in review_elems:
                    review_data = self._extract_review(elem)
                    if review_data:
                        all_reviews.append(review_data)

                self.logger.info(f"Scraped page {page} for {company} on G2: {len(review_elems)} reviews")
                page += 1
                time.sleep(5)  # Increased rate limiting

            except requests.RequestException as e:
                self.logger.error(f"Error scraping G2 page {page}: {e}")
                break

        # Filter by date
        filtered_reviews = date_utils.filter_reviews_by_date(all_reviews, start_date, end_date)
        self.logger.info(f"Filtered {len(filtered_reviews)} reviews for date range {start_date} to {end_date}")
        return filtered_reviews, product_slug