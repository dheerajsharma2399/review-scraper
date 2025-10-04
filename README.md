# SaaS Review Scraper

A Python-based web scraper that extracts product reviews from **G2**, **Capterra**, and **TrustRadius** for a specified company and time period.
This project is a command-line tool for scraping product reviews from leading SaaS review platforms: **G2**, **Capterra**, and **TrustRadius**. It allows you to gather reviews for a specific company within a defined date range and saves the results in a structured JSON format.

## Features

- ✅ Scrape reviews from **three major sources**: G2, Capterra, and TrustRadius
- ✅ Filter reviews by **date range**
- ✅ Export to **clean JSON format**
- ✅ **Merge results** from multiple sources
- ✅ Handles **pagination** automatically
- ✅ Robust **error handling** and logging
- ✅ **Rate limiting** to respect websites
- **Multi-Source Scraping**: Collects data from G2, Capterra, and TrustRadius.
- **Date Filtering**: Narrows down reviews to a specific start and end date.
- **JSON Export**: Outputs clean, well-structured JSON files.
- **Merged Reporting**: Generates a consolidated report when scraping from multiple sources.
- **Automatic Pagination**: Navigates through review pages automatically.
- **Reliable Operation**: Features robust error handling and detailed logging.
- **Polite Scraping**: Includes built-in delays to respect website servers.

## Project Structure

```
saas-review-scraper/
├── scraper.py                  # Main entry point
├── scrapers/
│   ├── __init__.py
│   ├── __init__.py 
│   ├── g2_scraper.py          # G2 scraping logic
│   ├── capterra_scraper.py    # Capterra scraping logic
│   └── trustradius_scraper.py # TrustRadius scraping logic (BONUS)
├── utils/
│   ├── __init__.py
│   ├── date_utils.py          # Date validation utilities
│   ├── json_exporter.py       # JSON export functions
│   └── logger.py              # Logging configuration
├── output/                     # Generated JSON files (auto-created)
├── requirements.txt
└── README.md
```

## Installation

### Prerequisites
### Requirements
- Python 3.8 or higher
- pip package manager

### Setup
### Steps

1. **Clone or download the project**
1. **Get the Code**
```bash
cd saas-review-scraper
```

2. **Create a virtual environment** (recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Basic Command Structure

```bash
python scraper.py --company "COMPANY_NAME" \
                  --start-date "YYYY-MM-DD" \
                  --end-date "YYYY-MM-DD" \
                  --source "SOURCE"
```

### Parameters

| Parameter | Required | Description | Example |
|-----------|----------|-------------|---------|
| `--company` | ✅ Yes | Company/product name to scrape | `"Salesforce"` |
| `--start-date` | ✅ Yes | Start date (YYYY-MM-DD) | `"2024-01-01"` |
| `--end-date` | ✅ Yes | End date (YYYY-MM-DD) | `"2024-12-31"` |
| `--source` | ✅ Yes | Source(s) to scrape: `g2`, `capterra`, `trustradius` (comma-separated) | `"g2,capterra"` |
| `--output-dir` | ❌ No | Output directory (default: `output`) | `"results"` |
| `--max-pages` | ❌ No | Max pages per source (default: 10) | `20` |

### Examples

#### Single Source (G2)
```bash
python scraper.py --company "Slack" \
                  --start-date "2024-01-01" \
                  --end-date "2024-12-31" \
                  --source "g2"
```

#### Multiple Sources
```bash
python scraper.py --company "Salesforce" \
                  --start-date "2024-06-01" \
                  --end-date "2024-09-30" \
                  --source "g2,capterra,trustradius"
```

#### All Three Sources with Custom Settings
```bash
python scraper.py --company "HubSpot" \
                  --start-date "2024-01-01" \
                  --end-date "2024-03-31" \
                  --source "g2,capterra,trustradius" \
                  --output-dir "my_results" \
                  --max-pages 15
```

## Output Format
## Implementation Notes

- **Technology Stack**: Built with Python 3.8+, using `requests` for HTTP fetching and `BeautifulSoup` for HTML parsing. No browser automation (Selenium) or external APIs—pure custom scraping.
- **Modern Practices**: Type hints, pathlib for paths, structured logging, argparse for CLI, PEP 8 compliance.
- **Rate Limiting**: 2-second delays between requests; handles 429 errors with 60s wait. Respect site terms to avoid bans.
- **Maintenance**: CSS selectors in scrapers may break if sites update. Inspect pages and adjust selectors in respective scraper.py files.
- **Logging**: Outputs to console and `logs/scraper.log` for debugging.
- **Edge Cases**: Handles no reviews, invalid dates/companies, network errors via logging and graceful exits.

### Individual Source File
The scraper creates a JSON file for each source:

**Filename:** `{company}_{source}_{start_date}_to_{end_date}.json`

**Example:** `salesforce_g2_2024-01-01_to_2024-12-31.json`

```json
{
  "company": "Salesforce",
  "source": "g2",
  "product_slug": "salesforce",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "total_reviews": 150,
  "reviews": [
    {
      "title": "Great CRM Solution",
      "review": "Salesforce has transformed our sales process...",
      "date": "2024-06-15",
      "date_raw": "June 15, 2024",
      "rating": 4.5,
      "reviewer_name": "John D.",
      "verified": true,
      "helpful_count": 12
    }
  ],
  "scrape_timestamp": "2024-09-30T14:30:00"
}
```

### Merged File (Multiple Sources)
When scraping from multiple sources, an additional merged file is created:

**Filename:** `{company}_all_sources_{start_date}_to_{end_date}.json`

```json
{
  "company": "Salesforce",
  "sources": ["g2", "capterra", "trustradius"],
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "total_reviews": 450,
  "reviews_by_source": {
    "g2": 150,
    "capterra": 200,
    "trustradius": 100
  },
  "reviews": [...],
  "merge_timestamp": "2024-09-30T14:35:00"
}
```

### Review Fields

Each review contains:

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Review title/headline |
| `review` | string | Full review text |
| `date` | string | Review date (YYYY-MM-DD) |
| `date_raw` | string | Original date string from source |

## Troubleshooting

- **No Reviews Found**: Verify company name spelling and existence on the site. Check date range for relevance. Review logs in `logs/scraper.log` for search or parsing errors.
- **Scraping Errors**: Websites frequently update HTML structures. If no data is scraped, inspect the page source (e.g., via browser dev tools) and update CSS selectors in the corresponding scraper.py file (e.g., g2_scraper.py).
- **Rate Limiting/Bans**: If encountering 429 errors frequently, increase the sleep time in scrapers (default 2s) or implement proxies. Always respect robots.txt and terms of service.
- **Installation Issues**: Ensure Python 3.8+ and run `pip install -r requirements.txt`. Virtual environment recommended.
- **Date Parsing Failures**: Raw dates from sites vary; if filtering misses reviews, check `date_raw` in output and adjust parse_date in date_utils.py if needed.
- **Merged JSON Empty**: Ensure multiple sources return data; check individual JSONs first.
- **General**: Run with `--max-pages 1` for quick tests. Logs provide detailed error info.