from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import ValidationError
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies import get_current_user_optional
from app.models import EnvironmentalObservation, Place, User
from app.schemas import EnvironmentalObservationCreate

router = APIRouter()
MAX_DISPLAYED_OBSERVATIONS = 100


def _admin_or_redirect(request: Request, db: Session) -> User | RedirectResponse:
    user = get_current_user_optional(request, db)
    if user is None:
        return RedirectResponse("/login?msg=Please+log+in+to+access+monitoring", status_code=303)
    if user.role != "admin":
        return RedirectResponse("/dashboard?msg=Environmental+monitoring+is+for+authorized+staff", status_code=303)
    return user


def _observation_form_context(
    request: Request,
    db: Session,
    user: User,
    *,
    form_data: dict[str, Any] | None = None,
    errors: list[str] | None = None,
    selected_place: int | None = None,
):
    places = db.exec(
        select(Place).where(Place.status == "approved").order_by(Place.place_name)
    ).all()
    statement = (
        select(EnvironmentalObservation)
        .order_by(EnvironmentalObservation.observed_at.desc())
        .limit(MAX_DISPLAYED_OBSERVATIONS)
    )
    if selected_place is not None:
        statement = statement.where(EnvironmentalObservation.place_id == selected_place)
    observations = db.exec(statement).all()
    observation_rows = []
    for observation in observations:
        place = db.get(Place, observation.place_id)
        observation_rows.append(
            {
                "record": observation,
                "place_name": place.place_name if place else "Removed destination",
            }
        )
    return request.app.state.templates.TemplateResponse(
        "environmental.html",
        {
            "request": request,
            "user": user,
            "places": places,
            "observations": observation_rows,
            "form_data": form_data or {},
            "errors": errors or [],
            "selected_place": selected_place,
        },
    )


@router.get("/environmental", response_class=HTMLResponse)
def environmental_page(
    request: Request,
    db: Session = Depends(get_db),
    place_id: int | None = None,
):
    user = _admin_or_redirect(request, db)
    if isinstance(user, RedirectResponse):
        return user
    return _observation_form_context(request, db, user, selected_place=place_id)


@router.post("/environmental/observations", response_class=HTMLResponse)
async def create_environmental_observation(
    request: Request,
    db: Session = Depends(get_db),
):
    user = _admin_or_redirect(request, db)
    if isinstance(user, RedirectResponse):
        return user

    form = await request.form()
    form_data = {key: value for key, value in form.items() if value != ""}
    try:
        observation_data = EnvironmentalObservationCreate.model_validate(form_data)
    except ValidationError as exc:
        errors = [
            f"{'.'.join(str(part) for part in error['loc'])}: {error['msg']}"
            for error in exc.errors()
        ]
        try:
            selected_place = int(form_data["place_id"])
        except (KeyError, ValueError):
            selected_place = None
        response = _observation_form_context(
            request,
            db,
            user,
            form_data=form_data,
            errors=errors,
            selected_place=selected_place,
        )
        response.status_code = 422
        return response

    place = db.get(Place, observation_data.place_id)
    if place is None or place.status != "approved":
        response = _observation_form_context(
            request,
            db,
            user,
            form_data=form_data,
            errors=["Choose an approved destination."],
            selected_place=observation_data.place_id,
        )
        response.status_code = 422
        return response

    db.add(
        EnvironmentalObservation(
            **observation_data.model_dump(),
            entered_by=user.id,
        )
    )
    db.commit()
    return RedirectResponse(
        "/environmental?msg=Monitoring+observation+saved",
        status_code=303,
    )
