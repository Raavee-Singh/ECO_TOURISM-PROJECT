from __future__ import annotations

from pathlib import Path

import jwt
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from passlib.context import CryptContext
from sqlmodel import Session, select

from app.config import settings
from app.database import engine, get_db, init_db
from app.dependencies import get_current_user, get_current_user_optional
from app.models import Place, Review, SavedPlace, User
from app.routers.bookings import router as bookings_router
from app.routers.budget import router as budget_router
from app.routers.complaints import router as complaints_router
from app.routers.dashboard import router as dashboard_router
from app.routers.environmental import router as environmental_router
from app.routers.places import router as places_router
from app.routers.reviews import router as reviews_router
from app.seed import seed_data

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))

app = FastAPI(title=settings.app_name)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.state.templates = templates

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
def startup_event():
    init_db()
    with Session(engine) as session:
        seed_data(session)


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    places = db.exec(select(Place).where(Place.status == "approved").order_by(Place.place_name).limit(6)).all()
    reviews = db.exec(select(Review).order_by(Review.created_at.desc()).limit(5)).all()
    categories = ["wildlife", "forest", "western ghats", "trekking", "hill", "mountain", "waterfall", "backwaters"]
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": user, "places": places, "reviews": reviews, "categories": categories},
    )


@app.get("/register")
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    return templates.TemplateResponse("register.html", {"request": request, "user": user})


@app.post("/register")
def register_user(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    existing = db.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(name=name, email=email, phone=phone, hashed_password=pwd_context.hash(password), role="visitor", is_active=True)
    db.add(user)
    db.commit()
    return RedirectResponse("/login?msg=Registration+successful", status_code=303)


@app.get("/login")
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    return templates.TemplateResponse("login.html", {"request": request, "user": user})


@app.post("/login")
def login_user(
    request: Request,
    db: Session = Depends(get_db),
    email: str = Form(...),
    password: str = Form(...),
):
    user = db.exec(select(User).where(User.email == email)).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = jwt.encode({"sub": str(user.id), "role": user.role}, settings.secret_key, algorithm=settings.algorithm)
    response = RedirectResponse("/?msg=Logged+in+successfully", status_code=303)
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return response


@app.post("/logout")
def logout(request: Request):
    response = RedirectResponse("/", status_code=303)
    response.delete_cookie("access_token")
    return response


@app.get("/profile")
def profile(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    places = db.exec(select(SavedPlace).where(SavedPlace.user_id == user.id)).all()
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "saved_places": [db.get(Place, p.place_id) for p in places if p.place_id]},
    )


@app.post("/profile")
def update_profile(
    request: Request,
    db: Session = Depends(get_db),
    name: str = Form(...),
    phone: str = Form(...),
    user: User = Depends(get_current_user),
):
    user.name = name
    user.phone = phone
    db.add(user)
    db.commit()
    return RedirectResponse("/profile?msg=Profile+updated", status_code=303)


@app.post("/change-password")
def change_password(
    request: Request,
    db: Session = Depends(get_db),
    current_password: str = Form(...),
    new_password: str = Form(...),
    user: User = Depends(get_current_user),
):
    if not pwd_context.verify(current_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.hashed_password = pwd_context.hash(new_password)
    db.add(user)
    db.commit()
    return RedirectResponse("/profile?msg=Password+updated", status_code=303)


@app.exception_handler(404)
def not_found(request: Request, exc):
    with Session(engine) as db:
        user = get_current_user_optional(request, db)
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request, "user": user},
        status_code=404,
    )


app.include_router(places_router)
app.include_router(reviews_router)
app.include_router(bookings_router)
app.include_router(complaints_router)
app.include_router(budget_router)
app.include_router(dashboard_router)
app.include_router(environmental_router)
