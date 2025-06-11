from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime, date


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1, max_length=100)
    locality: str = Field(..., min_length=1, max_length=100)
    cuisine: str = Field(..., min_length=1, max_length=100)
    rating: Optional[float] = Field(default=0.0, ge=0.0, le=5.0)
    total_capacity: Optional[int] = Field(default=50, ge=1, le=500)
    phone: Optional[str] = None
    email: Optional[str] = None
    opening_time: Optional[str] = Field(default="09:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    closing_time: Optional[str] = Field(default="23:00", pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantResponse(RestaurantBase):
    id: str
    vacancy: int
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class RestaurantSearchRequest(BaseModel):
    city: str = Field(..., min_length=1)
    locality: str = Field(..., min_length=1)
    cuisine: str = Field(..., min_length=1)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            if parsed_date < date.today():
                raise ValueError("Date must be today or in the future")
            return v
        except ValueError as e:
            raise ValueError(f"Invalid date format or date in past: {e}")

class RestaurantSearchResponse(BaseModel):
    id: str
    name: str
    address: str
    rating: float
    cuisine: str
    available_slots: Optional[List[str]] = []


class ReservationRequest(BaseModel):
    restaurant_id: str = Field(..., min_length=1)
    date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    time: str = Field(..., pattern=r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    guests: int = Field(..., ge=1, le=20)
    user_name: str = Field(..., min_length=1, max_length=100)
    user_phone: str = Field(...)

    @field_validator('date')
    @classmethod
    def validate_date(cls, v):
        try:
            parsed_date = datetime.strptime(v, "%Y-%m-%d").date()
            if parsed_date < date.today():
                raise ValueError("Date must be today or in the future")
            return v
        except ValueError as e:
            raise ValueError(f"Invalid date format or date in past: {e}")


class ReservationResponse(BaseModel):
    reservation_id: str
    table_number: str
    status: str
    instructions: str
    alternate_slots: Optional[List[str]] = []


class ReservationErrorResponse(BaseModel):
    status: str
    error_message: str


class ErrorResponse(BaseModel):
    error: str
    details: str


