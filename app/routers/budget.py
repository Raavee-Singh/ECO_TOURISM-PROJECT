from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import BudgetPlan, User

router = APIRouter()


@router.get("/budget")
def budget_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user:
        plans = db.exec(select(BudgetPlan).where(BudgetPlan.user_id == user.id).order_by(BudgetPlan.created_at.desc())).all()
    else:
        plans = []
    return request.app.state.templates.TemplateResponse("budget.html", {"request": request, "user": user, "plans": plans})


@router.post("/budget")
def save_budget(
    request: Request,
    db: Session = Depends(get_db),
    days: int = Form(1),
    travelers: int = Form(1),
    stay_cost: float = Form(0.0),
    entry_cost: float = Form(0.0),
    food_cost: float = Form(0.0),
    transport_cost: float = Form(0.0),
    guide_cost: float = Form(0.0),
    activity_cost: float = Form(0.0),
    misc_cost: float = Form(0.0),
    user: User = Depends(get_current_user),
):
    total = sum([stay_cost, entry_cost, food_cost, transport_cost, guide_cost, activity_cost, misc_cost])
    plan = BudgetPlan(
        user_id=user.id,
        days=days,
        travelers=travelers,
        stay_cost=stay_cost,
        entry_cost=entry_cost,
        food_cost=food_cost,
        transport_cost=transport_cost,
        guide_cost=guide_cost,
        activity_cost=activity_cost,
        misc_cost=misc_cost,
        total_cost=total,
    )
    db.add(plan)
    db.commit()
    return RedirectResponse("/budget?msg=Budget+plan+saved", status_code=303)
