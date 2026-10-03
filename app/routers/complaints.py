from __future__ import annotations

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import Complaint, User

router = APIRouter()


@router.get("/complaints")
def complaints_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user and user.role == "admin":
        complaints = db.exec(select(Complaint).order_by(Complaint.created_at.desc())).all()
    elif user:
        complaints = db.exec(select(Complaint).where(Complaint.user_id == user.id).order_by(Complaint.created_at.desc())).all()
    else:
        complaints = []
    return request.app.state.templates.TemplateResponse("complaints.html", {"request": request, "user": user, "complaints": complaints})


@router.post("/complaints")
def submit_complaint(
    request: Request,
    db: Session = Depends(get_db),
    category: str = Form(...),
    subject: str = Form(...),
    description: str = Form(...),
    place_id: int = Form(0),
    user: User = Depends(get_current_user),
):
    complaint = Complaint(
        user_id=user.id,
        place_id=place_id or None,
        category=category,
        subject=subject,
        description=description,
        status="open",
    )
    db.add(complaint)
    db.commit()
    return RedirectResponse("/complaints?msg=Complaint+submitted", status_code=303)


@router.post("/complaints/{complaint_id}/respond")
async def respond_to_complaint(complaint_id: int, request: Request, db: Session = Depends(get_db), admin: User = Depends(get_current_user)):
    if admin.role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")
    complaint = db.get(Complaint, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    admin_response = (await request.form()).get("admin_response", "").strip()
    if not admin_response:
        raise HTTPException(status_code=400, detail="An admin response is required")
    complaint.admin_response = admin_response
    complaint.status = "resolved"
    db.add(complaint)
    db.commit()
    return RedirectResponse("/complaints?msg=Complaint+resolved", status_code=303)
