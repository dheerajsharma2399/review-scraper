#!/usr/bin/env python3
"""
Review Scraper Script
Scrapes product reviews from G2, Capterra, or TrustRadius for a given company and date range.
Usage: python main.py --company "Slack" --start "2023-01-01" --end "2024-01-01" --source "g2" [--no-headless]
"""

import argparse
import json
from datetime import datetime
import os
from scrapers.g2_scraper import scrape_g2_reviews
from scrapers.capterra_scraper import scrape_capterra_reviews
from scrapers.trustradius_scraper import scrape_trustradius_reviews

def validate_dates(start_date, end_date):
    """Validate date format YYYY-MM-DD and ensure start <= end."""
    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        if start > end:
            raise ValueError("Start date must be before or equal to end date.")
        return start, end
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD. {e}")

def filter_reviews_by_date(reviews, start_date, end_date):
    """Filter reviews within the date range."""
    start, end = validate_dates(start_date, end_date)
    filtered = []
    for review in reviews:
        if review['date'] is None:
            continue
        try:
            review_date = datetime.strptime(review['date'], "%Y-%m-%d")
            if start <= review_date <= end:
                filtered.append(review)
        except ValueError:
            # Skip invalid dates
            continue
    return filtered

def main():
    parser = argparse.ArgumentParser(description="Scrape product reviews from review sites.")
    parser.add_argument("--company", required=True, help="Company name (e.g., Slack)")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", required=True, choices=["g2", "capterra", "trustradius"], help="Review source")
    parser.add_argument("--no-headless", action="store_true", help="Run browser in non-headless mode for debugging")
    
    args = parser.parse_args()
    
    try:
        validate_dates(args.start, args.end)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Map source to scraper function
    scrapers = {
        "g2": scrape_g2_reviews,
        "capterra": scrape_capterra_reviews,
        "trustradius": scrape_trustradius_reviews,
    }
    
    scraper = scrapers.get(args.source)
    if not scraper:
        print(f"Error: Unsupported source {args.source}")
        return
    
    print(f"Scraping {args.company} reviews from {args.source.upper()}...")
    
    # Call scraper with no_headless flag
    reviews = scraper(args.company, args.start, args.end, no_headless=args.no_headless)
    
    # Filter by date
    reviews = filter_reviews_by_date(reviews, args.start, args.end)
    
    if not reviews:
        print("No reviews found in the specified date range.")
        reviews = []  # Ensure empty list for JSON
    
    # Generate output filename
    filename = f"{args.company.lower().replace(' ', '_')}_{args.source}_{args.start}_{args.end}_reviews.json"
    output_path = os.path.join(os.getcwd(), filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"reviews": reviews}, f, indent=2, ensure_ascii=False)
    
    print(f"Reviews saved to {output_path} ({len(reviews)} reviews)")

if __name__ == "__main__":
    main()