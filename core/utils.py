"""
Utility functions for SEW-TRACK project.
"""

from datetime import datetime, date
from typing import Optional


def generate_code(prefix: str, sequence: int) -> str:
    """
    Generate a code with prefix and sequence number.
    
    Example: generate_code('TASK', 123) -> 'TASK-00123'
    """
    return f"{prefix}-{sequence:05d}"


def calculate_date_range(year: int, month: int) -> tuple[date, date]:
    """
    Calculate the start and end dates for a given month.
    
    Returns: (start_date, end_date)
    """
    start_date = date(year, month, 1)
    
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)
    
    return start_date, end_date


def format_currency(amount: float, currency: str = 'UZS') -> str:
    """
    Format amount as currency string.
    
    Example: format_currency(1234567.89) -> '1,234,567.89 UZS'
    """
    return f"{amount:,.2f} {currency}"


def get_current_period() -> str:
    """
    Get current period name.
    
    Example: 'November 2024'
    """
    now = datetime.now()
    return now.strftime('%B %Y')


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    """
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ZeroDivisionError):
        return default


def truncate_string(text: str, length: int = 50, suffix: str = '...') -> str:
    """
    Truncate a string to a specified length.
    
    Example: truncate_string('Hello World', 5) -> 'Hello...'
    """
    if len(text) <= length:
        return text
    return text[:length].rstrip() + suffix

