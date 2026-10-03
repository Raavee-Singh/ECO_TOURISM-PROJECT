from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import Place, Review, User

router = APIRouter()


@router.get("/reviews")
def reviews_page(request: Request, db: Session = Depends(get_db), rating: int = 0):
    user = get_current_user_optional(request, db)
    statement = select(Review).order_by(Review.created_at.desc())
    if rating:
        statement = statement.where(Review.rating == rating)
    reviews = db.exec(statement).all()
    review_rows = []
    for review in reviews:
        reviewer = db.get(User, review.user_id)
        review_rows.append({
            "id": review.id,
            "title": review.title,
            "comment": review.comment,
            "rating": review.rating,
            "user": {"name": reviewer.name if reviewer else "Visitor"},
        })
    places = db.exec(select(Place).where(Place.status == "approved")).all()
    return request.app.state.templates.TemplateResponse(
        "reviews.html",
        {"request": request, "user": user, "reviews": review_rows, "places": places, "rating": rating},
    )


@router.post("/places/{place_id}/reviews")
def add_review(
    place_id: int,
    request: Request,
    db: Session = Depends(get_db),
    title: str = Form(...),
    comment: str = Form(...),
    rating: int = Form(...),
):
    user = get_current_user(request, db)
    existing = db.exec(select(Review).where(Review.user_id == user.id, Review.place_id == place_id)).first()
    if existing:
        return RedirectResponse(f"/places/{place_id}?msg=You+already+reviewed+this+place", status_code=303)
    review = Review(user_id=user.id, place_id=place_id, rating=rating, title=title, comment=comment)
    db.add(review)
    db.commit()
    return RedirectResponse(f"/places/{place_id}?msg=Review+added", status_code=303)


@router.post("/reviews/{review_id}/delete")
def delete_review(review_id: int, request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    review = db.get(Review, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    if user.role != "admin" and review.user_id != user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own review")
    db.delete(review)
    db.commit()
    return RedirectResponse("/reviews?msg=Review+deleted", status_code=303)
