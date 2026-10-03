from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import Activity, Guide, Place, Review, SavedPlace, Stay, User

router = APIRouter()


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


@router.get("/places/add")
def add_place_form(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user is None:
        return RedirectResponse("/login?msg=Please+log+in+to+add+a+place", status_code=303)
    return request.app.state.templates.TemplateResponse("add_place.html", {"request": request, "user": user})


@router.post("/places/add")
def create_place(
    request: Request,
    db: Session = Depends(get_db),
    place_name: str = Form(...),
    location: str = Form(...),
    category: str = Form(...),
    description: str = Form(...),
    entry_fee: float = Form(...),
    visiting_hours: str = Form(...),
    district: Optional[str] = Form(None),
    latitude: Optional[float] = Form(None),
    longitude: Optional[float] = Form(None),
    image_url: Optional[str] = Form(None),
    best_season: Optional[str] = Form(None),
    eco_rating: Optional[float] = Form(None),
):
    user = get_current_user_optional(request, db)
    if user is None:
        raise HTTPException(status_code=401, detail="Please log in first.")
    if not place_name or not location or not category or not description:
        raise HTTPException(status_code=400, detail="Missing required place information.")
    if entry_fee < 0:
        raise HTTPException(status_code=400, detail="Entry fee cannot be negative.")
    if latitude is not None and not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90.")
    if longitude is not None and not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180.")
    place = Place(
        place_name=place_name,
        location=location,
        category=category,
        description=description,
        entry_fee=entry_fee,
        visiting_hours=visiting_hours,
        status="approved" if user.role == "admin" else "pending",
        district=district,
        latitude=latitude,
        longitude=longitude,
        image_url=image_url,
        best_season=best_season,
        eco_rating=eco_rating,
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
