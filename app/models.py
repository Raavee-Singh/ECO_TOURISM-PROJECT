from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(index=True, unique=True)
    phone: str
    hashed_password: str
    role: str = "visitor"
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Place(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    place_name: str
    location: str
    category: str
    description: str
    entry_fee: float = 0.0
    visiting_hours: str = "9:00 AM - 5:00 PM"
    status: str = "pending"
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    best_season: Optional[str] = None
    eco_rating: Optional[float] = None
    created_by: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Stay(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    place_id: int = Field(foreign_key="place.id")
    name: str
    type: str
    price_per_night: float
    amenities: str
    rooms_available: int = 1
    eco_certified: bool = False
    contact: str
    image_url: Optional[str] = None


class Guide(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    place_id: Optional[int] = Field(default=None, foreign_key="place.id")
    name: str
    languages: str
    experience_years: int = 1
    specialization: str
    price_per_day: float
    rating_avg: float = 0.0
    is_available: bool = True
    bio: str


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    place_id: int = Field(foreign_key="place.id")
    name: str
    description: str
    price_per_person: float
    duration_hours: float = 1.0
    difficulty: str = "easy"
    max_group_size: int = 10
    season: str = "all-season"


class Booking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    booking_type: str
    item_id: int
    place_id: int = Field(foreign_key="place.id")
    start_date: str
    end_date: str
    guests: int = 1
    total_price: float = 0.0
    status: str = "pending"
    reference_code: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    place_id: int = Field(foreign_key="place.id")
    stay_id: Optional[int] = Field(default=None, foreign_key="stay.id")
    guide_id: Optional[int] = Field(default=None, foreign_key="guide.id")
    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id")
    rating: int
    title: str
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Complaint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    place_id: Optional[int] = Field(default=None, foreign_key="place.id")
    category: str
    subject: str
    description: str
    status: str = "open"
    admin_response: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class BudgetPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    place_id: Optional[int] = Field(default=None, foreign_key="place.id")
    days: int = 1
    travelers: int = 1
    stay_cost: float = 0.0
    entry_cost: float = 0.0
    food_cost: float = 0.0
    transport_cost: float = 0.0
    guide_cost: float = 0.0
    activity_cost: float = 0.0
    misc_cost: float = 0.0
    total_cost: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SavedPlace(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    place_id: int = Field(foreign_key="place.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class EnvironmentalObservation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    place_id: int = Field(foreign_key="place.id", index=True)
    entered_by: int = Field(foreign_key="user.id")
    observed_at: datetime = Field(index=True)
    data_basis: str

    trail_zone: Optional[str] = None
    visitor_count: int = 0
    group_size: Optional[int] = None
    visit_duration_minutes: Optional[float] = None

    waste_total_kg: Optional[float] = None
    waste_plastic_kg: Optional[float] = None
    waste_organic_kg: Optional[float] = None
    waste_recyclable_kg: Optional[float] = None
    waste_collected_kg: Optional[float] = None
    waste_disposal_method: Optional[str] = None

    water_consumed_liters: Optional[float] = None
    water_available_liters: Optional[float] = None
    accommodation_water_liters: Optional[float] = None
    wastewater_liters: Optional[float] = None

    vehicle_count: Optional[int] = None
    vehicle_type: Optional[str] = None
    transport_distance_km: Optional[float] = None
    transport_mode: Optional[str] = None
    passenger_count: Optional[int] = None
    estimated_transport_emissions_kg: Optional[float] = None

    temperature_c: Optional[float] = None
    rainfall_mm: Optional[float] = None
    weather: Optional[str] = None
    trail_condition: Optional[str] = None
    vegetation_condition: Optional[str] = None
    water_availability_condition: Optional[str] = None

    wildlife_sightings: Optional[int] = None
    sensitive_species_or_area: Optional[str] = None
    wildlife_activity: Optional[str] = None
    disturbance_reports: Optional[int] = None
    seasonal_sensitivity: Optional[str] = None

    local_guides: Optional[int] = None
    local_homestays: Optional[int] = None
    local_vendors: Optional[int] = None
    community_employment: Optional[int] = None
    local_tourism_revenue_inr: Optional[float] = None

    notes: Optional[str] = None
