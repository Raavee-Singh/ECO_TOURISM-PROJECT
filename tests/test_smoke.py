from pathlib import Path
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from uuid import uuid4

from app.database import engine, init_db
from app.models import Booking, Complaint, EnvironmentalObservation, Place, Stay, User
from app.main import app
from app.seed import DESTINATIONS, seed_data

client = TestClient(app)


def setup_module():
    init_db()


def test_home_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "EcoTour Karnataka" in response.text
    assert "Explore Responsibly" in response.text
    assert "Explore Destinations" in response.text
    assert "Plan Your Visit" in response.text
    assert 'aria-controls="main-navigation"' in response.text
    assert "scene__ridge--far" in response.text
    assert "data-theme-choice=\"sunset\"" in response.text


def test_scene_stylesheet_is_served():
    response = client.get("/static/css/scene.css")
    assert response.status_code == 200
    assert "--sky-top" in response.text
    assert ".scene-toggle__menu" in response.text


def test_premium_stylesheet_is_served():
    response = client.get("/static/css/style.css")
    assert response.status_code == 200
    assert ".hero-banner::before" in response.text
    assert "backdrop-filter: blur(12px)" in response.text


def test_register_and_login_flow():
    email = f"{uuid4().hex}@example.com"
    response = client.post("/register", data={
        "name": "Test Visitor",
        "email": email,
        "phone": "9999999999",
        "password": "secret123",
        "confirm_password": "secret123",
    }, follow_redirects=False)
    assert response.status_code in (200, 303)

    login = client.post("/login", data={
        "email": email,
        "password": "secret123",
    }, follow_redirects=False)
    assert login.status_code in (200, 303)
    assert "access_token" in login.headers.get("set-cookie", "")


def test_routes_render_and_unknown_path_is_404():
    for path in ("/places", "/reviews", "/stays", "/guides", "/activities", "/budget", "/complaints"):
        response = client.get(path)
        assert response.status_code == 200, path
    assert client.get("/not-a-real-page").status_code == 404


def test_seed_catalog_uses_karnataka_nature_destinations():
    with Session(engine) as db:
        seed_data(db)
        places = db.exec(select(Place).where(Place.status == "approved")).all()
        names = {place.place_name for place in places}

    assert len(DESTINATIONS) == 22
    assert {destination["place_name"] for destination in DESTINATIONS} <= names
    assert "Mysore Palace" not in names
    assert "Bandipur National Park" in names
    assert "Kudremukh National Park" in names
    assert "Savandurga" in names


def test_every_seeded_destination_has_a_local_jpeg():
    image_dir = Path(__file__).resolve().parents[1] / "app" / "static" / "images" / "places"
    places_page = client.get("/places")
    assert places_page.status_code == 200

    for destination in DESTINATIONS:
        filename = destination["place_name"].lower().replace(" ", "-") + ".jpg"
        image = image_dir / filename
        assert image.is_file(), filename
        assert image.read_bytes().startswith(b"\xff\xd8"), filename
        asset_url = f"/static/images/places/{filename}"
        assert f'data-local-src="{asset_url}"' in places_page.text
        response = client.get(asset_url)
        assert response.status_code == 200, filename
        assert response.headers["content-type"].startswith("image/jpeg"), filename
        head_response = client.head(asset_url)
        assert head_response.status_code == 200, filename
        assert head_response.headers["content-type"].startswith("image/jpeg"), filename


def test_authenticated_user_can_open_destination_form():
    client.post("/login", data={"email": "visitor@ecotourism.in", "password": "visitor123"})
    response = client.get("/places/add")

    assert response.status_code == 200
    assert "Add a new place" in response.text
    assert 'action="/places/add"' in response.text


def test_visitor_can_submit_destination_with_optional_fields_blank():
    client.post("/login", data={"email": "visitor@ecotourism.in", "password": "visitor123"})
    place_name = f"Submission test {uuid4().hex}"
    response = client.post(
        "/places/add",
        data={
            "place_name": place_name,
            "location": "Karnataka",
            "category": "forest",
            "description": "A test destination submitted with optional fields blank.",
            "entry_fee": "",
            "visiting_hours": "",
            "district": "",
            "latitude": "",
            "longitude": "",
            "image_url": "",
            "best_season": "",
            "eco_rating": "",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"].startswith("/places/")
    with Session(engine) as db:
        place = db.exec(select(Place).where(Place.place_name == place_name)).first()
        assert place is not None
        assert place.status == "pending"
        assert place.entry_fee == 0
        assert place.visiting_hours == "Check current official access notices"
        assert place.latitude is None
        assert place.longitude is None
        assert place.eco_rating is None
        db.delete(place)
        db.commit()


def test_destination_form_shows_validation_errors():
    client.post("/login", data={"email": "visitor@ecotourism.in", "password": "visitor123"})
    response = client.post(
        "/places/add",
        data={
            "place_name": "Invalid rating test",
            "location": "Karnataka",
            "category": "forest",
            "description": "The rating is outside the permitted range.",
            "eco_rating": "6",
        },
    )

    assert response.status_code == 400
    assert "Eco rating must be between 1 and 5." in response.text
    assert 'value="6"' in response.text


def test_booking_uses_server_price_and_unique_reference():
    with Session(engine) as db:
        user = db.exec(select(User).where(User.email == "visitor@ecotourism.in")).first()
        stay = db.exec(select(Stay)).first()
        assert user is not None and stay is not None

    client.post("/login", data={"email": user.email, "password": "visitor123"})
    response = client.post(
        "/bookings/create",
        data={
            "booking_type": "stay",
            "item_id": str(stay.id),
            "place_id": str(stay.place_id),
            "start_date": "2027-01-10",
            "end_date": "2027-01-12",
            "guests": "2",
            "rooms": "1",
            "total_price": "0.01",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    with Session(engine) as db:
        booking = db.exec(
            select(Booking)
            .where(Booking.user_id == user.id)
            .order_by(Booking.created_at.desc())
        ).first()
        assert booking is not None
        assert booking.total_price == stay.price_per_night * 2
        assert booking.reference_code.startswith("ECO-")


def test_admin_can_respond_to_complaint():
    client.post("/login", data={"email": "visitor@ecotourism.in", "password": "visitor123"})
    submitted = client.post(
        "/complaints",
        data={"category": "safety", "subject": "Test report", "description": "Checking admin response."},
        follow_redirects=False,
    )
    assert submitted.status_code == 303
    with Session(engine) as db:
        complaint = db.exec(
            select(Complaint)
            .where(Complaint.subject == "Test report")
            .order_by(Complaint.created_at.desc())
        ).first()
        assert complaint is not None
        complaint_id = complaint.id

    client.post("/login", data={"email": "admin@ecotourism.in", "password": "admin123"})
    response = client.post(
        f"/complaints/{complaint_id}/respond",
        data={"admin_response": "We have reviewed the report."},
        follow_redirects=False,
    )
    assert response.status_code == 303
    with Session(engine) as db:
        complaint = db.get(Complaint, complaint_id)
        assert complaint.status == "resolved"
        assert complaint.admin_response == "We have reviewed the report."


def test_environmental_monitoring_is_admin_only_and_validates_observations():
    visitor_login = client.post(
        "/login",
        data={"email": "visitor@ecotourism.in", "password": "visitor123"},
        follow_redirects=False,
    )
    assert visitor_login.status_code == 303
    visitor_page = client.get("/environmental", follow_redirects=False)
    assert visitor_page.status_code == 303
    assert visitor_page.headers["location"].startswith("/dashboard")

    client.post(
        "/login",
        data={"email": "admin@ecotourism.in", "password": "admin123"},
        follow_redirects=False,
    )
    page = client.get("/environmental")
    assert page.status_code == 200
    assert "Record an observation" in page.text

    with Session(engine) as db:
        place = db.exec(select(Place).where(Place.status == "approved")).first()
        admin = db.exec(select(User).where(User.email == "admin@ecotourism.in")).first()
        assert place is not None and admin is not None
        place_id = place.id
        admin_id = admin.id

    response = client.post(
        "/environmental/observations",
        data={
            "place_id": str(place_id),
            "observed_at": "2026-10-03T10:30",
            "data_basis": "mixed",
            "trail_zone": "Research test zone",
            "visitor_count": "42",
            "waste_total_kg": "18.5",
            "water_consumed_liters": "250",
            "estimated_transport_emissions_kg": "12.4",
            "trail_condition": "moderate",
            "wildlife_sightings": "3",
            "disturbance_reports": "1",
            "local_guides": "5",
            "notes": "Waste value includes estimated collection data.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    with Session(engine) as db:
        observation = db.exec(
            select(EnvironmentalObservation)
            .where(EnvironmentalObservation.trail_zone == "Research test zone")
        ).first()
        assert observation is not None
        assert observation.entered_by == admin_id
        assert observation.visitor_count == 42
        assert observation.waste_total_kg == 18.5
        assert observation.data_basis == "mixed"

    history_page = client.get(f"/environmental?place_id={place_id}")
    assert history_page.status_code == 200
    assert "Research test zone" in history_page.text

    invalid = client.post(
        "/environmental/observations",
        data={
            "place_id": str(place_id),
            "observed_at": "2026-10-03T10:30",
            "data_basis": "measured",
            "visitor_count": "-1",
        },
    )
    assert invalid.status_code == 422
    assert "greater than or equal to 0" in invalid.text
