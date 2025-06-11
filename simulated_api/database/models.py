from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from simulated_api.database.setup import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(String, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    address = Column(Text, nullable=False)
    city = Column(String(100), nullable=False, index=True)
    locality = Column(String(100), nullable=False, index=True)
    cuisine = Column(String(100), nullable=False, index=True)
    rating = Column(Float, default=0.0)
    total_capacity = Column(Integer, default=50)
    vacancy = Column(Integer, default=50)  # Available seats
    phone = Column(String(20))
    email = Column(String(100))
    opening_time = Column(String(5), default="09:00")  # HH:MM format
    closing_time = Column(String(5), default="23:00")  # HH:MM format
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    reservations = relationship("Reservation", back_populates="restaurant")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(String, primary_key=True, index=True)
    restaurant_id = Column(String, ForeignKey("restaurants.id"), nullable=False)
    date = Column(String(10), nullable=False)  # YYYY-MM-DD
    time = Column(String(5), nullable=False)  # HH:MM
    guests = Column(Integer, nullable=False)
    user_name = Column(String(100), nullable=False)
    user_phone = Column(String(20), nullable=False)
    table_number = Column(String(10))
    status = Column(String(20), default="confirmed")  # confirmed, cancelled, completed
    instructions = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationship
    restaurant = relationship("Restaurant", back_populates="reservations")