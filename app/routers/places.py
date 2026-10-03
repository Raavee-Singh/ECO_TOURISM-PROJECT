from __future__ import annotations

import math
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import Activity, Guide, Place, Review, SavedPlace, Stay, User

router = APIRouter()


def _parse_optional_float(value: Optional[str], field_name: str) -> Optional[float]:
    if value is None or not value.strip():
        return None
    try:
        number = float(value)
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a number.") from exc
    if not math.isfinite(number):
        raise ValueError(f"{field_name} must be a finite number.")
    return number


def _place_query_filters(db: Session, category: str = "", district: str = "", query: str = ""):
    statement = select(Place).where(Place.status == "approved")
    if category:
        statement = statement.where(Place.category == category)
    if district:
        statement = statement.where(Place.district == district)
    if query:
        keyword = f"%{query}%"
        statement = statement.where(
            (Place.place_name.ilike(keyword))
            | (Place.location.ilike(keyword))
            | (Place.district.ilike(keyword))
            | (Place.description.ilike(keyword))
        )
    return db.exec(statement.order_by(Place.place_name)).all()


@router.get("/places")
def places_page(request: Request, db: Session = Depends(get_db), category: str = "", district: str = "", q: str = ""):
    user = get_current_user_optional(request, db)
    places = _place_query_filters(db, category=category, district=district, query=q)
    categories = ["wildlife", "forest", "western ghats", "trekking", "hill", "mountain", "waterfall", "backwaters"]
    districts = sorted({p.district for p in db.exec(select(Place).where(Place.status == "approved")).all() if p.district})
    return request.app.state.templates.TemplateResponse(
        "places.html",
        {"request": request, "user": user, "places": places, "categories": categories, "districts": districts, "category": category, "district": district, "q": q},
    )


@router.get("/places/add")
def add_place_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user is None:
        return RedirectResponse("/login?msg=Please+log+in+to+add+a+place", status_code=303)
    return request.app.state.templates.TemplateResponse(
        "add_place.html",
        {"request": request, "user": user},
    )


@router.get("/places/{place_id}")
def place_detail(request: Request, place_id: int, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    place = db.get(Place, place_id)
    if not place or (
        place.status != "approved"
        and (user is None or (user.role != "admin" and place.created_by != user.id))
    ):
        return request.app.state.templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "user": user},
            status_code=404,
        )
    reviews = db.exec(select(Review).where(Review.place_id == place_id).order_by(Review.created_at.desc())).all()
    review_rows = []
    for review in reviews:
        reviewer = db.get(User, review.user_id)
        review_rows.append({
            "id": review.id,
            "title": review.title,
            "comment": review.comment,
            "rating": review.rating,
            "user_id": review.user_id,
            "user": {"name": reviewer.name if reviewer else "Visitor"},
        })
    stays = db.exec(select(Stay).where(Stay.place_id == place_id)).all()
    guides = db.exec(select(Guide).where(Guide.place_id == place_id)).all()
    activities = db.exec(select(Activity).where(Activity.place_id == place_id)).all()
    average_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0
    return request.app.state.templates.TemplateResponse(
        "place_detail.html",
        {"request": request, "user": user, "place": place, "reviews": review_rows, "stays": stays, "guides": guides, "activities": activities, "average_rating": average_rating},
    )


@router.post("/places/add")
def create_place(
    request: Request,
    db: Session = Depends(get_db),
    place_name: str = Form(""),
    location: str = Form(""),
    category: str = Form(""),
    description: str = Form(""),
    entry_fee: str = Form(""),
    visiting_hours: str = Form(""),
    district: str = Form(""),
    latitude: str = Form(""),
    longitude: str = Form(""),
    image_url: str = Form(""),
    best_season: str = Form(""),
    eco_rating: str = Form(""),
):
    user = get_current_user_optional(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Please log in first.")
    form_data = {
        "place_name": place_name.strip(),
        "location": location.strip(),
        "category": category.strip(),
        "description": description.strip(),
        "entry_fee": entry_fee.strip(),
        "visiting_hours": visiting_hours.strip(),
        "district": district.strip(),
        "latitude": latitude.strip(),
        "longitude": longitude.strip(),
        "image_url": image_url.strip(),
        "best_season": best_season.strip(),
        "eco_rating": eco_rating.strip(),
    }
    error = None
    entry_fee_value = 0.0
    latitude_value = None
    longitude_value = None
    eco_rating_value = None
    if not form_data["place_name"] or not form_data["location"] or not form_data["category"] or not form_data["description"]:
        error = "Place name, location, category, and description are required."
    else:
        try:
            entry_fee_value = _parse_optional_float(entry_fee, "Entry fee") or 0.0
            latitude_value = _parse_optional_float(latitude, "Latitude")
            longitude_value = _parse_optional_float(longitude, "Longitude")
            eco_rating_value = _parse_optional_float(eco_rating, "Eco rating")
            if entry_fee_value < 0:
                error = "Entry fee cannot be negative."
            elif latitude_value is not None and not -90 <= latitude_value <= 90:
                error = "Latitude must be between -90 and 90."
            elif longitude_value is not None and not -180 <= longitude_value <= 180:
                error = "Longitude must be between -180 and 180."
            elif eco_rating_value is not None and not 1 <= eco_rating_value <= 5:
                error = "Eco rating must be between 1 and 5."
        except ValueError as exc:
            error = str(exc)
    if error:
        return request.app.state.templates.TemplateResponse(
            "add_place.html",
            {"request": request, "user": user, "form_data": form_data, "error": error},
            status_code=400,
        )
    place = Place(
        place_name=form_data["place_name"],
        location=form_data["location"],
        category=form_data["category"],
        description=form_data["description"],
        entry_fee=entry_fee_value,
        visiting_hours=form_data["visiting_hours"] or "Check current official access notices",
        status="approved" if user.role == "admin" else "pending",
        district=form_data["district"] or None,
        latitude=latitude_value,
        longitude=longitude_value,
        image_url=form_data["image_url"] or None,
        best_season=form_data["best_season"] or None,
        eco_rating=eco_rating_value,
        created_by=user.id,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return RedirectResponse(f"/places/{place.id}?msg=Place+submitted+successfully", status_code=303)


@router.post("/places/{place_id}/save")
def save_place(place_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    place = db.get(Place, place_id)
    if place is None or place.status != "approved":
        raise HTTPException(status_code=404, detail="Approved place not found")
    existing = db.exec(select(SavedPlace).where(SavedPlace.user_id == user.id, SavedPlace.place_id == place_id)).first()
    if existing:
        return RedirectResponse(f"/places/{place_id}?msg=Already+saved", status_code=303)
    db.add(SavedPlace(user_id=user.id, place_id=place_id))
    db.commit()
    return RedirectResponse(f"/places/{place_id}?msg=Saved+to+wishlist", status_code=303)


@router.post("/places/{place_id}/approve")
def approve_place(place_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_user)):
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    place.status = "approved"
    db.add(place)
    db.commit()
    return RedirectResponse("/dashboard?msg=Place+approved", status_code=303)


@router.post("/places/{place_id}/reject")
def reject_place(place_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_user)):
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    place.status = "rejected"
    db.add(place)
    db.commit()
    return RedirectResponse("/dashboard?msg=Place+rejected", status_code=303)


@router.post("/places/{place_id}/delete")
def delete_place(place_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_user)):
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    place = db.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    db.delete(place)
    db.commit()
    return RedirectResponse("/dashboard?msg=Place+deleted", status_code=303)


@router.get("/place-details")
def place_details_redirect(request: Request, db: Session = Depends(get_db)):
    first = db.exec(select(Place).where(Place.status == "approved")).first()
    if first is None:
        return RedirectResponse("/places", status_code=303)
    return RedirectResponse(f"/places/{first.id}", status_code=303)
