"""
Utility Functions
Helper functions for database operations and data manipulation.
"""

from datetime import datetime
from typing import Any, Dict, List
import json


def format_currency(amount: float, currency: str = "NGN") -> str:
    """Format amount as currency string."""
    return f"{currency} {amount:,.2f}"


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """Format datetime object as string."""
    if isinstance(date, datetime):
        return date.strftime(format_str)
    return str(date)


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
    """Parse date string to datetime object."""
    return datetime.strptime(date_str, format_str)


def get_full_name(first_name: str, last_name: str) -> str:
    """Get full name from first and last names."""
    return f"{first_name} {last_name}".strip()


def calculate_delivery_cost(distance_km: float, rate_per_km: float = 100) -> float:
    """Calculate delivery cost based on distance."""
    return distance_km * rate_per_km


def apply_discount(amount: float, discount_percent: float) -> float:
    """Apply discount percentage to an amount."""
    return amount * (1 - discount_percent / 100)


def calculate_order_total(subtotal: float, delivery_cost: float = 0, discount: float = 0) -> float:
    """Calculate order total with delivery and discount."""
    total = subtotal + delivery_cost
    if discount > 0:
        total = apply_discount(total, discount)
    return round(total, 2)


def rows_to_dicts(cursor_description: List, rows: List) -> List[Dict]:
    """Convert cursor rows to list of dictionaries."""
    if not cursor_description or not rows:
        return []
    
    column_names = [desc[0] for desc in cursor_description]
    return [dict(zip(column_names, row)) for row in rows]


def dict_to_json(data: Dict, indent: int = 2) -> str:
    """Convert dictionary to formatted JSON string."""
    return json.dumps(data, indent=indent, default=str)


def json_to_dict(json_str: str) -> Dict:
    """Convert JSON string to dictionary."""
    return json.loads(json_str)


def paginate_results(results: List, page: int = 1, page_size: int = 10) -> Dict:
    """Paginate results."""
    total = len(results)
    total_pages = (total + page_size - 1) // page_size
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    return {
        'page': page,
        'page_size': page_size,
        'total': total,
        'total_pages': total_pages,
        'results': results[start_idx:end_idx]
    }


def sanitize_input(value: str) -> str:
    """Sanitize user input to prevent SQL injection."""
    if not isinstance(value, str):
        return str(value)
    # Remove potentially dangerous characters
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
    for char in dangerous_chars:
        value = value.replace(char, "")
    return value.strip()


def validate_email(email: str) -> bool:
    """Validate email format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate Nigerian phone number format."""
    import re
    # Nigerian phone format: +234 or 0, followed by 10 digits
    pattern = r'^(\+234|0)[0-9]{10}$'
    return re.match(pattern, phone.replace(" ", "").replace("-", "")) is not None


def retry_on_exception(func, max_retries: int = 3, delay_seconds: float = 1):
    """Retry a function call on exception."""
    import time
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)