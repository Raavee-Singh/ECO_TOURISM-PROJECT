from __future__ import annotations

from passlib.context import CryptContext
from sqlmodel import Session, select

from app.models import Activity, Booking, BudgetPlan, Complaint, Guide, Place, Review, SavedPlace, Stay, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_data(session: Session):
    if session.exec(select(User).where(User.email == "admin@ecotourism.in")).first():
        return

    admin = User(name="Admin User", email="admin@ecotourism.in", phone="9876543210", hashed_password=pwd_context.hash("admin123"), role="admin")
    visitor = User(name="Aisha Nair", email="visitor@ecotourism.in", phone="9123456780", hashed_password=pwd_context.hash("visitor123"), role="visitor")
    guide_user = User(name="Nikhil Kumar", email="guide@ecotourism.in", phone="9988776655", hashed_password=pwd_context.hash("guide123"), role="guide")
    session.add_all([admin, visitor, guide_user])
    session.commit()

    place1 = Place(
        place_name="Bandipur National Park",
        location="Bandipur",
        category="wildlife",
        description="A biodiverse forest with elephant corridors and a scenic tiger reserve.",
        entry_fee=200,
        visiting_hours="6:00 AM - 6:00 PM",
        status="approved",
        district="Chamarajanagar",
        latitude=11.81,
        longitude=76.64,
        image_url="https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
        best_season="Winter",
        eco_rating=4.8,
        created_by=admin.id,
    )
    place2 = Place(
        place_name="Jog Falls",
        location="Shimoga",
        category="waterfall",
        description="One of the tallest waterfalls in India, surrounded by forested hills.",
        entry_fee=150,
        visiting_hours="9:00 AM - 5:30 PM",
        status="approved",
        district="Shivamogga",
        latitude=14.23,
        longitude=74.82,
        image_url="https://images.unsplash.com/photo-1501785888041-af3ef285b470",
        best_season="Monsoon",
        eco_rating=4.5,
        created_by=admin.id,
    )
    place3 = Place(
        place_name="Mysore Palace",
        location="Mysuru",
        category="heritage",
        description="A grand palace with heritage architecture and landscaped gardens.",
        entry_fee=70,
        visiting_hours="10:00 AM - 5:30 PM",
        status="approved",
        district="Mysuru",
        latitude=12.3,
        longitude=76.65,
        image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945",
        best_season="Winter",
        eco_rating=4.4,
        created_by=admin.id,
    )
    session.add_all([place1, place2, place3])
    session.commit()

    stay1 = Stay(place_id=place1.id, name="Forest Canopy Homestay", type="homestay", price_per_night=1800, amenities="Breakfast, nature walk, parking", rooms_available=4, eco_certified=True, contact="+91 98765 43210", image_url="https://images.unsplash.com/photo-1505693416388-ac5ce068fe85")
    stay2 = Stay(place_id=place2.id, name="Mist Valley Eco Resort", type="eco-resort", price_per_night=2600, amenities="Pool, local cuisine, guided hikes", rooms_available=3, eco_certified=True, contact="+91 98765 12345", image_url="https://images.unsplash.com/photo-1494526585095-c41746248156")
    session.add_all([stay1, stay2])

    guide1 = Guide(user_id=guide_user.id, place_id=place1.id, name="Krishna Rao", languages="Kannada, English", experience_years=8, specialization="Wildlife tracking", price_per_day=2200, rating_avg=4.7, is_available=True, bio="Wildlife naturalist focused on forest ecology and responsible travel.")
    guide2 = Guide(user_id=guide_user.id, place_id=place2.id, name="Leena Fernandes", languages="Kannada, Hindi, English", experience_years=5, specialization="Waterfall trails", price_per_day=1800, rating_avg=4.5, is_available=True, bio="Leads eco-friendly treks and cultural storytelling sessions.")
    session.add_all([guide1, guide2])

    activity1 = Activity(place_id=place1.id, name="Elephant Valley Safari", description="Low-impact safari designed for biodiversity observation.", price_per_person=950, duration_hours=3, difficulty="moderate", max_group_size=8, season="winter")
    activity2 = Activity(place_id=place2.id, name="Canoe Ride and Viewpoint Trek", description="Scenic hillside adventure with local flora interpretation.", price_per_person=700, duration_hours=2, difficulty="easy", max_group_size=12, season="monsoon")
    session.add_all([activity1, activity2])

    booking = Booking(user_id=visitor.id, booking_type="stay", item_id=stay1.id, place_id=place1.id, start_date="2026-11-10", end_date="2026-11-12", guests=2, total_price=3600, status="confirmed", reference_code="ECO-1001")
    session.add(booking)

    review1 = Review(user_id=visitor.id, place_id=place1.id, rating=5, title="Amazing biodiversity", comment="Beautiful forest with calm roads and responsible tourism practices.")
    review2 = Review(user_id=admin.id, place_id=place2.id, rating=4, title="Scenic and well maintained", comment="The view was memorable and the local nature guides were knowledgeable.")
    session.add_all([review1, review2])

    complaint = Complaint(user_id=visitor.id, place_id=place1.id, category="safety", subject="Trail signage issue", description="The signage near the elephant path is unclear and needs better guidance.", status="open")
    plan = BudgetPlan(user_id=visitor.id, place_id=place1.id, days=2, travelers=2, stay_cost=3600, entry_cost=400, food_cost=2000, transport_cost=1200, guide_cost=2200, activity_cost=1900, misc_cost=500, total_cost=11800)
    saved = SavedPlace(user_id=visitor.id, place_id=place2.id)
    session.add_all([complaint, plan, saved])
    session.commit()
