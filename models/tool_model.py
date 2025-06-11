from pydantic import BaseModel, Field, model_validator
from datetime import datetime, date


class RestaurantSearchArgs(BaseModel):
    city: str = Field(..., description="City name, must not be empty")
    locality: str = Field(..., description="Locality or area within the city")
    cuisine: str = Field(..., description="Cuisine type (e.g., Italian, Indian)")
    date: str = Field(..., description="Reservation date in YYYY-MM-DD format (must be a valid future date)")
    time: str = Field(..., description="Time in HH:MM format (24-hour)")


class TableReserveArgs(BaseModel):
    restaurant_id: str = Field(..., description="Unique ID of the restaurant")
    date: str = Field(..., description="Reservation date in YYYY-MM-DD format (must be a valid future date)")
    time: str = Field(..., description="Reservation time in HH:MM format (24-hour)")
    guests: int = Field(..., description="Number of guests to reserve for")
    user_name: str = Field(..., description="Name of the person making the reservation")
    user_phone: str = Field(..., description="Phone number of the user (in international format, e.g., +91...)")


    @model_validator(mode="after")
    def validate_datetime(cls, values: 'TableReserveArgs') -> 'TableReserveArgs':
        try:
            # Validate date
            res_date = datetime.strptime(values.date, "%Y-%m-%d").date()
            if res_date <= date.today():
                raise ValueError("Reservation date must be in the future (not today or past).")

            # Validate time
            datetime.strptime(values.time, "%H:%M")

        except ValueError as e:
            raise ValueError(f"Invalid input: {e}")

        return values


