from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str = Field(min_length=6)
    confirm_password: str = Field(min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


class PlaceCreate(BaseModel):
    place_name: str
    location: str
    category: str
    description: str
    entry_fee: float = 0
    visiting_hours: str = "9:00 AM - 5:00 PM"
    status: str = "pending"
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_url: Optional[str] = None
    best_season: Optional[str] = None
    eco_rating: Optional[float] = None


class ReviewCreate(BaseModel):
    place_id: int
    rating: int = Field(ge=1, le=5)
    title: str
    comment: str


class BookingCreate(BaseModel):
    booking_type: str
    item_id: int
    place_id: int
    start_date: str
    end_date: str
    guests: int = 1
    total_price: float = 0.0


class ComplaintCreate(BaseModel):
    place_id: Optional[int] = None
    category: str
    subject: str
    description: str


class BudgetPlanCreate(BaseModel):
    place_id: Optional[int] = None
    days: int = 1
    travelers: int = 1
    stay_cost: float = 0.0
    entry_cost: float = 0.0
    food_cost: float = 0.0
    transport_cost: float = 0.0
    guide_cost: float = 0.0
    activity_cost: float = 0.0
    misc_cost: float = 0.0


class EnvironmentalObservationCreate(BaseModel):
    place_id: int = Field(gt=0)
    observed_at: datetime
    data_basis: Literal["measured", "estimated", "mixed"]
    trail_zone: Optional[str] = Field(default=None, max_length=120)
    visitor_count: int = Field(default=0, ge=0)
    group_size: Optional[int] = Field(default=None, ge=0)
    visit_duration_minutes: Optional[float] = Field(default=None, ge=0)

    waste_total_kg: Optional[float] = Field(default=None, ge=0)
    waste_plastic_kg: Optional[float] = Field(default=None, ge=0)
    waste_organic_kg: Optional[float] = Field(default=None, ge=0)
    waste_recyclable_kg: Optional[float] = Field(default=None, ge=0)
    waste_collected_kg: Optional[float] = Field(default=None, ge=0)
    waste_disposal_method: Optional[str] = Field(default=None, max_length=120)

    water_consumed_liters: Optional[float] = Field(default=None, ge=0)
    water_available_liters: Optional[float] = Field(default=None, ge=0)
    accommodation_water_liters: Optional[float] = Field(default=None, ge=0)
    wastewater_liters: Optional[float] = Field(default=None, ge=0)

    vehicle_count: Optional[int] = Field(default=None, ge=0)
    vehicle_type: Optional[str] = Field(default=None, max_length=120)
    transport_distance_km: Optional[float] = Field(default=None, ge=0)
    transport_mode: Optional[Literal["shared", "private", "mixed"]] = None
    passenger_count: Optional[int] = Field(default=None, ge=0)
    estimated_transport_emissions_kg: Optional[float] = Field(default=None, ge=0)

    temperature_c: Optional[float] = Field(default=None, ge=-90, le=60)
    rainfall_mm: Optional[float] = Field(default=None, ge=0)
    weather: Optional[str] = Field(default=None, max_length=120)
    trail_condition: Optional[Literal["good", "moderate", "poor", "closed"]] = None
    vegetation_condition: Optional[str] = Field(default=None, max_length=120)
    water_availability_condition: Optional[Literal["adequate", "limited", "scarce", "unknown"]] = None

    wildlife_sightings: Optional[int] = Field(default=None, ge=0)
    sensitive_species_or_area: Optional[str] = Field(default=None, max_length=240)
    wildlife_activity: Optional[str] = Field(default=None, max_length=240)
    disturbance_reports: Optional[int] = Field(default=None, ge=0)
    seasonal_sensitivity: Optional[Literal["low", "medium", "high", "unknown"]] = None

    local_guides: Optional[int] = Field(default=None, ge=0)
    local_homestays: Optional[int] = Field(default=None, ge=0)
    local_vendors: Optional[int] = Field(default=None, ge=0)
    community_employment: Optional[int] = Field(default=None, ge=0)
    local_tourism_revenue_inr: Optional[float] = Field(default=None, ge=0)

    notes: Optional[str] = Field(default=None, max_length=2000)
