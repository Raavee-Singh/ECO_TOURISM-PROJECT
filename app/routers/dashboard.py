from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user_optional
from app.models import Booking, Complaint, Place, Review, SavedPlace

router = APIRouter()


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user is None:
        return RedirectResponse("/login?msg=Please+log+in+first", status_code=303)
    places = db.exec(select(Place).order_by(Place.created_at.desc())).all()
    bookings = db.exec(select(Booking).where(Booking.user_id == user.id).order_by(Booking.created_at.desc())).all()
    complaints = db.exec(select(Complaint).order_by(Complaint.created_at.desc())).all() if user.role == "admin" else []
    saved_place_rows = db.exec(select(SavedPlace).where(SavedPlace.user_id == user.id)).all()
    saved_places = []
    for saved in saved_place_rows:
        place = db.get(Place, saved.place_id)
        saved_places.append({"place_name": place.place_name if place else "Saved place"})
    reviews = db.exec(select(Review).where(Review.user_id == user.id).order_by(Review.created_at.desc())).all()
    return request.app.state.templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "user": user, "places": places, "bookings": bookings, "complaints": complaints, "saved_places": saved_places, "reviews": reviews},
    )
