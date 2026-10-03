from __future__ import annotations

from passlib.context import CryptContext
from sqlmodel import Session, select

from app.models import (
    Activity,
    Booking,
    BudgetPlan,
    Complaint,
    Guide,
    Place,
    Review,
    SavedPlace,
    Stay,
    User,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DESTINATIONS = [
    {
        "place_name": "Anthargange",
        "location": "Kolar",
        "category": "trekking",
        "description": "A rocky hill range known for volcanic rock formations, caves, spring water and forested slopes. The Karnataka Eco Tourism trail page recommends going with a certified nature guide; follow current access guidance.",
        "district": "Kolar",
    },
    {
        "place_name": "Bandipur National Park",
        "location": "Bandipur",
        "category": "wildlife",
        "description": "A protected forest landscape in southern Karnataka and part of the Nilgiri Biosphere Reserve. Wildlife viewing is subject to Forest Department rules, permitted routes and seasonal closures.",
        "district": "Chamarajanagar",
    },
    {
        "place_name": "Bhadra Tiger Reserve",
        "location": "Bhadra",
        "category": "western ghats",
        "description": "A Western Ghats forest and tiger-reserve landscape around the Bhadra catchment. Confirm which visitor activities, routes and permits are currently available with the Forest Department.",
        "district": "Chikkamagaluru",
    },
    {
        "place_name": "Biligiri Rangaswamy Temple Tiger Reserve",
        "location": "Biligiri Hills",
        "category": "forest",
        "description": "A protected forest landscape in the Biligiri hill range, linking the Western Ghats and Eastern Ghats. Access and visitor activities are subject to current reserve rules.",
        "district": "Chamarajanagar",
    },
    {
        "place_name": "Bidarakatte Eco Trail",
        "location": "Savandurga State Forest",
        "category": "trekking",
        "description": "An official Karnataka Eco Tourism trail near the Savandurga forest area, with rocky slopes, scrub vegetation and birdlife. Confirm the trailhead and current access before setting out.",
        "district": "Ramanagara",
    },
    {
        "place_name": "Chinaga Betta",
        "location": "Karnataka Eco Tourism trail",
        "category": "trekking",
        "description": "A named trail in the Karnataka Eco Tourism trail catalogue. Check the official trail listing for current route, access and seasonal information before visiting.",
        "district": None,
    },
    {
        "place_name": "Devarayanadurga",
        "location": "Devarayanadurga Hills",
        "category": "hill",
        "description": "A hilly, forested landscape in Tumakuru district, with hill trails and viewpoints. Karnataka Eco Tourism describes the area's dense green cover and surrounding wilderness; check local access notices.",
        "district": "Tumakuru",
    },
    {
        "place_name": "Dhamane-Tilari Eco Trail",
        "location": "Dhamane-Tilari",
        "category": "trekking",
        "description": "A named trail in the Karnataka Eco Tourism catalogue near the Tilari landscape. Confirm the precise trailhead, permitted access and current operating status through the official trail portal.",
        "district": "Belagavi",
    },
    {
        "place_name": "Halasagara Eco Trail",
        "location": "Halasagara",
        "category": "trekking",
        "description": "A trail listed by Karnataka Eco Tourism. Its public trail page has described the listing as coming soon; do not assume the route is open, and verify its status before planning a visit.",
        "district": None,
    },
    {
        "place_name": "Jog Falls",
        "location": "Sharavathi Valley",
        "category": "waterfall",
        "description": "A major waterfall on the Sharavathi River amid the Western Ghats landscape. Viewpoints and surrounding areas may have seasonal restrictions; check local notices and stay on marked paths.",
        "district": "Shivamogga",
    },
    {
        "place_name": "Kada View Point",
        "location": "Karnataka Eco Tourism trail",
        "category": "mountain",
        "description": "A named viewpoint trail in the Karnataka Eco Tourism catalogue. Check the official listing for location details, route access and current conditions before travelling.",
        "district": None,
    },
    {
        "place_name": "Kaiwara Betta",
        "location": "Kaiwara",
        "category": "trekking",
        "description": "A hill trail near Kaiwara in Chikkaballapur district. The Karnataka Eco Tourism listing describes steep, rugged terrain; plan for the conditions and follow current access guidance.",
        "district": "Chikkaballapur",
    },
    {
        "place_name": "Kali Tiger Reserve",
        "location": "Kali (Anshi-Dandeli)",
        "category": "western ghats",
        "description": "A protected forest and river landscape in the Western Ghats of Uttara Kannada. Wildlife viewing and outdoor activities are subject to current forest permissions and reserve rules.",
        "district": "Uttara Kannada",
    },
    {
        "place_name": "Kudremukh National Park",
        "location": "Kudremukh Range",
        "category": "western ghats",
        "description": "A Western Ghats national park known for its highland terrain, forested slopes and grassland landscapes. Trekking and visitor access require checking current Forest Department rules and permissions.",
        "district": "Chikkamagaluru",
    },
    {
        "place_name": "Makalidurga",
        "location": "Makalidurga Hill",
        "category": "trekking",
        "description": "A granite hill and fort trail near Doddaballapur. Karnataka Eco Tourism describes rocky terrain and views over the nearby lake; check current trail access and carry water.",
        "district": "Bengaluru Rural",
    },
    {
        "place_name": "Nagarahole National Park",
        "location": "Nagarahole",
        "category": "wildlife",
        "description": "A protected forest landscape in the Nilgiri Biosphere Reserve. Safari availability, routes and visitor access are managed under current Forest Department rules.",
        "district": "Kodagu",
    },
    {
        "place_name": "Ramadevara Betta",
        "location": "Ramanagara Hills",
        "category": "trekking",
        "description": "A hill and rocky outcrop in the Ramanagara landscape, listed among Karnataka Eco Tourism's nature trails. Confirm current access arrangements and respect local and forest rules.",
        "district": "Ramanagara",
    },
    {
        "place_name": "Sarvodaya Eco Trail",
        "location": "Sarvodaya Grama",
        "category": "trekking",
        "description": "A named destination in the Karnataka Eco Tourism trail catalogue near Sarvodaya Grama. Confirm the current route and operating status with the official trail portal before travel.",
        "district": "Ballari",
    },
    {
        "place_name": "Savandurga",
        "location": "Savandurga Hills",
        "category": "mountain",
        "description": "A prominent monolithic hill landscape near Magadi, with rocky slopes and forest at its base. Karnataka Eco Tourism advises visitors to use the designated trail and check current access guidance.",
        "district": "Ramanagara",
    },
    {
        "place_name": "Siddara Betta",
        "location": "Koratagere",
        "category": "trekking",
        "description": "A rocky hill trail in Koratagere taluk, Tumakuru district, with caves, natural springs and hill vegetation. Follow marked routes and current local guidance.",
        "district": "Tumakuru",
    },
    {
        "place_name": "Skandagiri",
        "location": "Kalavara Durga",
        "category": "trekking",
        "description": "A hill-fort trail in the Nandi hill range near Chikkaballapur. Karnataka Eco Tourism describes a route through scrub and rocky terrain; check current booking, entry and safety requirements.",
        "district": "Chikkaballapur",
    },
    {
        "place_name": "Tilari Backwater",
        "location": "Tilari",
        "category": "backwaters",
        "description": "A backwater destination listed in the Karnataka Eco Tourism trail catalogue. Verify the exact location, access arrangements and current visitor guidance before travelling.",
        "district": "Belagavi",
    },
]


def seed_data(session: Session):
    demo_users = {
        "admin@ecotourism.in": User(
            name="Admin User",
            email="admin@ecotourism.in",
            phone="9876543210",
            hashed_password=pwd_context.hash("admin123"),
            role="admin",
        ),
        "visitor@ecotourism.in": User(
            name="Aisha Nair",
            email="visitor@ecotourism.in",
            phone="9123456780",
            hashed_password=pwd_context.hash("visitor123"),
            role="visitor",
        ),
        "guide@ecotourism.in": User(
            name="Nikhil Kumar",
            email="guide@ecotourism.in",
            phone="9988776655",
            hashed_password=pwd_context.hash("guide123"),
            role="guide",
        ),
    }
    users = {}
    for email, demo_user in demo_users.items():
        users[email] = session.exec(select(User).where(User.email == email)).first()
        if users[email] is None:
            users[email] = demo_user
            session.add(demo_user)
    session.commit()

    admin = users["admin@ecotourism.in"]
    visitor = users["visitor@ecotourism.in"]
    guide_user = users["guide@ecotourism.in"]

    legacy_palace = session.exec(select(Place).where(Place.place_name == "Mysore Palace")).first()
    if legacy_palace:
        legacy_palace.status = "rejected"
        session.add(legacy_palace)
        session.commit()

    for destination in DESTINATIONS:
        place = session.exec(
            select(Place).where(Place.place_name == destination["place_name"])
        ).first()
        if place is None:
            place = Place(
                **destination,
                entry_fee=0,
                visiting_hours="Check current official access notices",
                status="approved",
                created_by=admin.id,
            )
        else:
            for field, value in destination.items():
                setattr(place, field, value)
            place.status = "approved"
            place.entry_fee = 0
            place.visiting_hours = "Check current official access notices"
            place.best_season = None
            place.eco_rating = None
            place.latitude = None
            place.longitude = None
            place.image_url = None
            place.created_by = place.created_by or admin.id
        session.add(place)
    session.commit()

    if session.exec(select(Stay)).first():
        return

    bandipur = session.exec(
        select(Place).where(Place.place_name == "Bandipur National Park")
    ).first()
    jog_falls = session.exec(select(Place).where(Place.place_name == "Jog Falls")).first()
    if bandipur is None or jog_falls is None:
        return

    stay1 = Stay(
        place_id=bandipur.id,
        name="Forest Canopy Homestay",
        type="homestay",
        price_per_night=1800,
        amenities="Breakfast, nature walk, parking",
        rooms_available=4,
        eco_certified=False,
        contact="+91 98765 43210",
        image_url=None,
    )
    stay2 = Stay(
        place_id=jog_falls.id,
        name="Mist Valley Eco Resort",
        type="eco-resort",
        price_per_night=2600,
        amenities="Local cuisine, guided hikes",
        rooms_available=3,
        eco_certified=False,
        contact="+91 98765 12345",
        image_url=None,
    )
    guide1 = Guide(
        user_id=guide_user.id,
        place_id=bandipur.id,
        name="Krishna Rao",
        languages="Kannada, English",
        experience_years=8,
        specialization="Wildlife tracking",
        price_per_day=2200,
        rating_avg=4.7,
        is_available=True,
        bio="Wildlife naturalist focused on forest ecology and responsible travel.",
    )
    guide2 = Guide(
        user_id=guide_user.id,
        place_id=jog_falls.id,
        name="Leena Fernandes",
        languages="Kannada, Hindi, English",
        experience_years=5,
        specialization="Waterfall trails",
        price_per_day=1800,
        rating_avg=4.5,
        is_available=True,
        bio="Leads eco-friendly treks and cultural storytelling sessions.",
    )
    session.add_all([stay1, stay2, guide1, guide2])
    session.commit()

    activity1 = Activity(
        place_id=bandipur.id,
        name="Elephant Valley Safari",
        description="Low-impact safari designed for biodiversity observation.",
        price_per_person=950,
        duration_hours=3,
        difficulty="moderate",
        max_group_size=8,
        season="winter",
    )
    activity2 = Activity(
        place_id=jog_falls.id,
        name="Canoe Ride and Viewpoint Trek",
        description="Scenic hillside adventure with local flora interpretation.",
        price_per_person=700,
        duration_hours=2,
        difficulty="easy",
        max_group_size=12,
        season="monsoon",
    )
    booking = Booking(
        user_id=visitor.id,
        booking_type="stay",
        item_id=stay1.id,
        place_id=bandipur.id,
        start_date="2026-11-10",
        end_date="2026-11-12",
        guests=2,
        total_price=3600,
        status="confirmed",
        reference_code="ECO-1001",
    )
    review1 = Review(
        user_id=visitor.id,
        place_id=bandipur.id,
        rating=5,
        title="Amazing biodiversity",
        comment="Beautiful forest with calm roads and responsible tourism practices.",
    )
    review2 = Review(
        user_id=admin.id,
        place_id=jog_falls.id,
        rating=4,
        title="Scenic and well maintained",
        comment="The view was memorable and the local nature guides were knowledgeable.",
    )
    complaint = Complaint(
        user_id=visitor.id,
        place_id=bandipur.id,
        category="safety",
        subject="Trail signage issue",
        description="The signage near the elephant path is unclear and needs better guidance.",
        status="open",
    )
    plan = BudgetPlan(
        user_id=visitor.id,
        place_id=bandipur.id,
        days=2,
        travelers=2,
        stay_cost=3600,
        entry_cost=400,
        food_cost=2000,
        transport_cost=1200,
        guide_cost=2200,
        activity_cost=1900,
        misc_cost=500,
        total_cost=11800,
    )
    saved = SavedPlace(user_id=visitor.id, place_id=jog_falls.id)
    session.add_all([activity1, activity2, booking, review1, review2, complaint, plan, saved])
    session.commit()
