from __future__ import annotations

from sqlmodel import Session

from app.models import Stay


def rooms_available(db: Session, stay_id: int, requested_rooms: int = 1) -> bool:
    stay = db.get(Stay, stay_id)
    if stay is None:
        return False
    return stay.rooms_available >= requested_rooms
