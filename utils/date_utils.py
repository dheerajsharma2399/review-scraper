from datetime import datetime
from dateutil import parser
from typing import List, Dict, Any

def validate_date(date_str: str) -> bool:
    """Validate if date string is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def parse_date(raw_date: str) -> str:
    """Parse raw date string to YYYY-MM-DD format."""
    try:
        parsed = parser.parse(raw_date)
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return None

def filter_reviews_by_date(reviews: List[Dict[str, Any]], start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Filter reviews to those within the start_date and end_date range."""
    if not validate_date(start_date) or not validate_date(end_date):
        raise ValueError("Invalid date format. Use YYYY-MM-DD.")
    
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    filtered = []
    for review in reviews:
        review_date_str = review.get("date")
        if review_date_str:
            parsed_date = parse_date(review_date_str)
            if parsed_date:
                review_date = datetime.strptime(parsed_date, "%Y-%m-%d")
                if start <= review_date <= end:
                    filtered.append(review)
    return filtered