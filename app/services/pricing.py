from __future__ import annotations

from app.models import Activity, Guide, Stay


def calculate_stay_total(stay: Stay, nights: int, rooms: int = 1) -> float:
    return float(stay.price_per_night) * max(nights, 1) * max(rooms, 1)


def calculate_guide_total(guide: Guide, days: int = 1) -> float:
    return float(guide.price_per_day) * max(days, 1)


def calculate_activity_total(activity: Activity, guests: int = 1) -> float:
    return float(activity.price_per_person) * max(guests, 1)
