from __future__ import annotations

from datetime import datetime


def is_valid_booking_date(start_date: str, end_date: str) -> bool:
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        return end >= start
    except ValueError:
        return False
