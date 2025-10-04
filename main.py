#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import os

from utils import logger as logger_module, date_utils, json_exporter
from scrapers.g2_scraper import G2Scraper
from scrapers.capterra_scraper import CapterraScraper
from scrapers.trustradius_scraper import TrustRadiusScraper

def main():
    parser = argparse.ArgumentParser(description="SaaS Review Scraper")
    parser.add_argument("--company", required=True, help="Company/product name")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", required=True, help="Source(s): g2,capterra,trustradius")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    parser.add_argument("--max-pages", type=int, default=10, help="Max pages per source")

    args = parser.parse_args()

    # Setup logger
    log = logger_module.setup_logger("scraper")

    # Validate dates
    if not date_utils.validate_date(args.start_date) or not date_utils.validate_date(args.end_date):
        log.error("Invalid date format. Use YYYY-MM-DD.")
        sys.exit(1)

    # Parse sources
    sources = [s.strip().lower() for s in args.source.split(",")]
    valid_sources = {"g2", "capterra", "trustradius"}
    invalid = set(sources) - valid_sources
    if invalid:
        log.error(f"Invalid sources: {invalid}. Valid: {valid_sources}")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Output directory: {output_dir}")

    all_source_reviews = {}
    for source in sources:
        log.info(f"Starting scrape for {source}")
        if source == "g2":
            scraper = G2Scraper(log)
            reviews, product_slug = scraper.scrape(args.company, args.start_date, args.end_date, args.max_pages)
        elif source == "capterra":
            scraper = CapterraScraper(log)
            reviews, product_slug = scraper.scrape(args.company, args.start_date, args.end_date, args.max_pages)
        elif source == "trustradius":
            scraper = TrustRadiusScraper(log)
            reviews, product_slug = scraper.scrape(args.company, args.start_date, args.end_date, args.max_pages)

        if reviews:
            # Add source to each review for merging
            for review in reviews:
                review["source"] = source
            all_source_reviews[source] = {"reviews": reviews, "product_slug": product_slug}
            log.info(f"Scraped {len(reviews)} reviews from {source}")
        else:
            log.warning(f"No reviews found for {source}")
            all_source_reviews[source] = {"reviews": [], "product_slug": args.company.lower().replace(" ", "-")}

        # Export individual
        single_path = output_dir / f"{args.company.lower().replace(' ', '_')}_{source}_{args.start_date}_to_{args.end_date}.json"
        json_exporter.export_single_source(
            args.company, source, all_source_reviews[source]["product_slug"],
            args.start_date, args.end_date, all_source_reviews[source]["reviews"], single_path
        )
        log.info(f"Exported {source} to {single_path}")

    # Merge if multiple sources
    if len(sources) > 1:
        merged_reviews = []
        reviews_by_source = {}
        for source, data in all_source_reviews.items():
            reviews_by_source[source] = len(data["reviews"])
            merged_reviews.extend(data["reviews"])

        merged_path = output_dir / f"{args.company.lower().replace(' ', '_')}_all_sources_{args.start_date}_to_{args.end_date}.json"
        json_exporter.export_merged(
            args.company, sources, args.start_date, args.end_date,
            merged_reviews, reviews_by_source, merged_path
        )
        log.info(f"Exported merged to {merged_path}")
        log.info(f"Total merged reviews: {len(merged_reviews)}")
    else:
        log.info("Single source, no merge needed")

    log.info("Scraping completed")

if __name__ == "__main__":
    main()