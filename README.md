# Review Scraper Script

## Overview
This Python script scrapes product reviews from G2, Capterra, and TrustRadius (bonus third source) for a specified company and date range. It outputs a JSON file with an array of reviews, each containing title, description, date, rating, and reviewer_name.

**Note:** This is a basic implementation using Selenium for dynamic sites. Selectors are placeholders based on common patterns and may need adjustment due to site changes or anti-bot measures (e.g., captchas observed during testing). Scraping may violate site Terms of Service; use responsibly, respect robots.txt, and implement rate limiting/proxies if needed. For production, consider official APIs if available.

## Setup
1. Ensure Python 3.8+ and Google Chrome are installed.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   This installs Selenium, BeautifulSoup4, and WebDriver Manager (auto-handles ChromeDriver).
3. No additional setup needed; ChromeDriver is managed automatically.

## Usage
Run the script via CLI:
```
python main.py --company "Slack" --start "2023-01-01" --end "2024-01-01" --source "g2"
```
- `--company`: Company/product name (e.g., "Slack").
- `--start` / `--end`: Date range in YYYY-MM-DD format.
- `--source`: One of "g2", "capterra", or "trustradius".

Output: A JSON file named `{company_slug}_{source}_{start}_{end}_reviews.json` in the current directory.

### Examples
- G2: `python main.py --company "Slack" --start "2023-01-01" --end "2024-01-01" --source "g2"`
- Capterra: `python main.py --company "Slack" --start "2023-01-01" --end "2024-01-01" --source "capterra"`
  - Note: Capterra requires a product ID; current placeholder uses Slack's ID (100000). For other companies, implement a search function in `scrapers/capterra_scraper.py` to dynamically find the ID/slug.
- TrustRadius: `python main.py --company "Slack" --start "2023-01-01" --end "2024-01-01" --source "trustradius"`

### Error Handling
- Invalid dates: Script validates YYYY-MM-DD format and start <= end.
- No reviews: Outputs message and empty JSON.
- Scraping errors: Prints errors (e.g., page not found, bot detection); returns empty list.
- For Capterra: If product ID is wrong, no reviews found; enhance with search.

## Implementation Details
- **Modular Design:** Separate scrapers in `scrapers/` for each source. Each uses headless Selenium with anti-detection options (user-agent, no webdriver flag).
- **Pagination:** Handles "next" buttons with delays to avoid bans.
- **Date Filtering:** Collects all reviews, filters by range in main.py (scrapers return dates as strings; parsing improved in filter).
- **Selectors:** Placeholders (e.g., `.review-title`); verify via browser dev tools. Sites are JS-heavy; run non-headless for debugging by removing `--headless`.
- **Bonus Source:** TrustRadius integrated with same interface. Specializes in B2B/SaaS reviews.
- **Limitations:** 
  - Anti-bot: May hit captchas (G2) or redirects; add proxies/rotating user-agents for robustness.
  - Capterra ID: Hardcoded for Slack; add search (e.g., navigate to https://www.capterra.com/search?query={company}, extract first result).
  - Date Parsing: Basic; enhance `parse_date` for site-specific formats (e.g., "Jan 2023" -> "2023-01-01").
  - No login support; some reviews may be gated.

## Sample JSON Output
For Slack on G2 (hypothetical data):
```json
{
  "reviews": [
    {
      "title": "Great collaboration tool",
      "description": "Slack has revolutionized our team communication...",
      "date": "2023-05-15",
      "rating": "4.5",
      "reviewer_name": "John Doe"
    },
    {
      "title": "Reliable and feature-rich",
      "description": "Integrations are top-notch, though pricing is high...",
      "date": "2023-07-20",
      "rating": "5.0",
      "reviewer_name": "Jane Smith"
    }
  ]
}
```

## Testing
- Run with sample inputs above.
- Check console for errors.
- Verify JSON file for structure/completeness.
- For development: Set `options.headless = False` in scrapers to watch browser.

## Legal and Ethical Notes
- Scraping public data is for educational purposes. Check each site's robots.txt and TOS.
- G2: Disallows automated access in TOS.
- Capterra: Similar restrictions.
- TrustRadius: May require permission for bulk scraping.
- Add delays (e.g., `time.sleep(5)`) between requests. Do not overload servers.

## Future Improvements
- Dynamic Capterra search for product ID.
- Advanced anti-detection (proxies, CAPTCHA solvers).
- Export to CSV in addition to JSON.
- Unit tests for parsing/filtering.

Deadline submission: Script ready within 48 hours. Contact for questions.