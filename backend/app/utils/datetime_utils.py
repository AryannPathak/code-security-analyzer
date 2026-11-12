"""Datetime utility helpers ensuring Python 3.11+ and 3.15+ compatibility."""
from datetime import datetime, timezone


def get_utc_now():
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(timezone.utc)
