import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

def export_single_source(
    company: str,
    source: str,
    product_slug: str,
    start_date: str,
    end_date: str,
    reviews: List[Dict[str, Any]],
    output_path: Path
) -> None:
    """Export reviews from a single source to JSON."""
    data = {
        "company": company,
        "source": source,
        "product_slug": product_slug,
        "date_range": {
            "start": start_date,
            "end": end_date
        },
        "total_reviews": len(reviews),
        "reviews": reviews,
        "scrape_timestamp": datetime.now().isoformat()
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def export_merged(
    company: str,
    sources: List[str],
    start_date: str,
    end_date: str,
    reviews: List[Dict[str, Any]],
    reviews_by_source: Dict[str, int],
    output_path: Path
) -> None:
    """Export merged reviews from multiple sources to JSON."""
    data = {
        "company": company,
        "sources": sources,
        "date_range": {
            "start": start_date,
            "end": end_date
        },
        "total_reviews": len(reviews),
        "reviews_by_source": reviews_by_source,
        "reviews": reviews,
        "merge_timestamp": datetime.now().isoformat()
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)