from __future__ import annotations

from typing import Any, Dict, List

from sqlmodel import Session, select

from app.models import Place


def search_places(db: Session, query: str = "", category: str = "", district: str = "") -> List[Place]:
    statement = select(Place).where(Place.status == "approved")
    if query:
        like = f"%{query}%"
        statement = statement.where(
            (Place.place_name.ilike(like))
            | (Place.location.ilike(like))
            | (Place.district.ilike(like))
            | (Place.description.ilike(like))
        )
    if category:
        statement = statement.where(Place.category == category)
    if district:
        statement = statement.where(Place.district == district)
    return db.exec(statement).all()
