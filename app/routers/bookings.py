from __future__ import annotations

from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import Activity, Booking, Guide, Place, Stay, User
from app.services.pricing import calculate_activity_total, calculate_guide_total, calculate_stay_total

router = APIRouter()


@router.get("/stays")
def stays_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    stays = db.exec(select(Stay)).all()
    return request.app.state.templates.TemplateResponse("stays.html", {"request": request, "user": user, "stays": stays})


@router.get("/guides")
def guides_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    guides = db.exec(select(Guide)).all()
    return request.app.state.templates.TemplateResponse("guides.html", {"request": request, "user": user, "guides": guides})


@router.get("/activities")
def activities_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    activities = db.exec(select(Activity)).all()
    return request.app.state.templates.TemplateResponse("activities.html", {"request": request, "user": user, "activities": activities})


@router.get("/bookings")
def bookings_page(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    bookings = db.exec(select(Booking).where(Booking.user_id == user.id).order_by(Booking.created_at.desc())).all()
    return request.app.state.templates.TemplateResponse("bookings.html", {"request": request, "user": user, "bookings": bookings})


@router.post("/bookings/create")
def create_booking(
    request: Request,
    db: Session = Depends(get_db),
    booking_type: str = Form(...),
    item_id: int = Form(...),
    place_id: int = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    guests: int = Form(1, ge=1),
    rooms: int = Form(1, ge=1),
    user: User = Depends(get_current_user),
):
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Dates must use YYYY-MM-DD format") from exc
    if end < start or (booking_type != "activity" and end == start):
        raise HTTPException(status_code=400, detail="End date must be after start date")
    place = db.get(Place, place_id)
    if place is None or place.status != "approved":
        raise HTTPException(status_code=404, detail="Approved place not found")

    if booking_type == "stay":
        item = db.get(Stay, item_id)
        if item is None or item.place_id != place_id:
            raise HTTPException(status_code=404, detail="Stay not found for this place")
        if item.rooms_available < rooms:
            raise HTTPException(status_code=409, detail="Not enough rooms are available")
        total_price = calculate_stay_total(item, (end - start).days, rooms)
    elif booking_type == "guide":
        item = db.get(Guide, item_id)
        if item is None or item.place_id != place_id or not item.is_available:
            raise HTTPException(status_code=404, detail="Available guide not found for this place")
        total_price = calculate_guide_total(item, (end - start).days)
    elif booking_type == "activity":
        item = db.get(Activity, item_id)
        if item is None or item.place_id != place_id:
            raise HTTPException(status_code=404, detail="Activity not found for this place")
        if guests > item.max_group_size:
            raise HTTPException(status_code=400, detail="Guest count exceeds the activity group limit")
        total_price = calculate_activity_total(item, guests)
    else:
        raise HTTPException(status_code=400, detail="Unsupported booking type")

    booking = Booking(
        user_id=user.id,
        booking_type=booking_type,
        item_id=item_id,
        place_id=place_id,
        start_date=start_date,
        end_date=end_date,
        guests=guests,
        total_price=total_price,
        status="pending",
        reference_code=f"ECO-{uuid4().hex[:12].upper()}",
    )
    db.add(booking)
    db.commit()
    return RedirectResponse("/bookings?msg=Booking+created", status_code=303)


@router.post("/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only cancel your own bookings")
    if booking.status == "cancelled":
        return RedirectResponse("/bookings?msg=Booking+already+cancelled", status_code=303)
    booking.status = "cancelled"
    db.add(booking)
    db.commit()
    return RedirectResponse("/bookings?msg=Booking+cancelled", status_code=303)
