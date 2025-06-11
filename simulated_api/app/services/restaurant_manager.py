import uuid
from datetime import datetime, timedelta
from typing import List, Union

from sqlalchemy import and_
from sqlalchemy.orm import Session

from simulated_api.app.models.pydantics import (
    RestaurantCreate, RestaurantSearchRequest, RestaurantSearchResponse,
    ReservationRequest, ReservationResponse, ReservationErrorResponse
)
from simulated_api.database.models import Restaurant, Reservation


class RestaurantManager:
    def __init__(self, db: Session):
        self.db = db

    def create_restaurant(self, restaurant_data: RestaurantCreate) -> Restaurant:
        """Create a new restaurant"""
        restaurant_id = f"res_{uuid.uuid4().hex[:8]}"

        db_restaurant = Restaurant(
            id=restaurant_id,
            **restaurant_data.model_dump(),
            vacancy=restaurant_data.total_capacity
        )
        self.db.add(db_restaurant)
        self.db.commit()
        self.db.refresh(db_restaurant)
        return db_restaurant

    def search_restaurants(self, search_params: RestaurantSearchRequest) -> List[RestaurantSearchResponse]:
        """Search restaurants based on criteria"""
        query = self.db.query(Restaurant).filter(
            and_(
                Restaurant.city.ilike(f"%{search_params.city}%"),
                Restaurant.locality.ilike(f"%{search_params.locality}%"),
                Restaurant.cuisine.ilike(f"%{search_params.cuisine}%"),
                Restaurant.is_active == True,
                Restaurant.vacancy > 0
            )
        ).order_by(Restaurant.rating.desc()).limit(5)

        restaurants = query.all()

        result = []
        for restaurant in restaurants:
            # Get available time slots if requested time is not available
            available_slots = self._get_available_slots(
                restaurant.id, search_params.date, search_params.time
            )

            result.append(RestaurantSearchResponse(
                id=restaurant.id,
                name=restaurant.name,
                address=restaurant.address,
                rating=restaurant.rating,
                cuisine=restaurant.cuisine,
                available_slots=available_slots
            ))

        return result

    def reserve_table(self, reservation_data: ReservationRequest) -> Union[
        ReservationResponse, ReservationErrorResponse]:
        """Reserve a table at a restaurant"""

        # Check if restaurant exists
        restaurant = self.db.query(Restaurant).filter(
            Restaurant.id == reservation_data.restaurant_id
        ).first()

        if not restaurant:
            return ReservationErrorResponse(
                status="invalid_restaurant",
                error_message=f"Restaurant with ID {reservation_data.restaurant_id} not found."
            )

        # Check if restaurant has capacity
        if restaurant.vacancy < reservation_data.guests:
            # Get alternative time slots
            alt_slots = self._get_available_slots(
                reservation_data.restaurant_id,
                reservation_data.date,
                reservation_data.time
            )

            return ReservationErrorResponse(
                status="no_availability",
                error_message=f"Not enough seats available. Required: {reservation_data.guests}, Available: {restaurant.vacancy}. Try these times: {', '.join(alt_slots) if alt_slots else 'No alternatives'}"
            )

        # Check for existing reservation at same time (table conflict)
        existing_reservation = self.db.query(Reservation).filter(
            and_(
                Reservation.restaurant_id == reservation_data.restaurant_id,
                Reservation.date == reservation_data.date,
                Reservation.time == reservation_data.time,
                Reservation.status == "confirmed"
            )
        ).first()

        if existing_reservation:
            alt_slots = self._get_available_slots(
                reservation_data.restaurant_id,
                reservation_data.date,
                reservation_data.time
            )

            return ReservationErrorResponse(
                status="time_unavailable",
                error_message=f"Time slot {reservation_data.time} is already booked. Available times: {', '.join(alt_slots) if alt_slots else 'No alternatives'}"
            )

        # Create reservation
        reservation_id = f"rev_{uuid.uuid4().hex[:8]}"
        table_number = str(uuid.uuid4().int % 20 + 1)  # Random table 1-20

        db_reservation = Reservation(
            id=reservation_id,
            restaurant_id=reservation_data.restaurant_id,
            date=reservation_data.date,
            time=reservation_data.time,
            guests=reservation_data.guests,
            user_name=reservation_data.user_name,
            user_phone=reservation_data.user_phone,
            table_number=table_number,
            status="confirmed",
            instructions=f"Arrive by {self._subtract_10_minutes(reservation_data.time)}. Table {table_number} reserved for {reservation_data.guests} guests."
        )

        # Update restaurant vacancy
        restaurant.vacancy -= reservation_data.guests

        self.db.add(db_reservation)
        self.db.commit()
        self.db.refresh(db_reservation)

        return ReservationResponse(
            reservation_id=reservation_id,
            table_number=table_number,
            status="confirmed",
            instructions=db_reservation.instructions,
            alternate_slots=[]
        )

    def _get_available_slots(self, restaurant_id: str, date: str, requested_time: str) -> List[str]:
        """Get available time slots for a restaurant on a specific date"""
        # Get restaurant opening hours
        restaurant = self.db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
        if not restaurant:
            return []

        # Generate time slots (every hour from opening to closing)
        opening_hour = int(restaurant.opening_time.split(':')[0])
        closing_hour = int(restaurant.closing_time.split(':')[0])

        available_slots = []
        for hour in range(opening_hour, min(closing_hour, 23)):  # Don't go past 23:00
            time_slot = f"{hour:02d}:00"

            # Check if this slot is available (no existing reservations)
            existing = self.db.query(Reservation).filter(
                and_(
                    Reservation.restaurant_id == restaurant_id,
                    Reservation.date == date,
                    Reservation.time == time_slot,
                    Reservation.status == "confirmed"
                )
            ).first()

            if not existing and time_slot != requested_time:
                available_slots.append(time_slot)

        return available_slots[:3]  # Return max 3 alternatives

    def _subtract_10_minutes(self, time_str: str) -> str:
        """Subtract 10 minutes from time string"""
        try:
            time_obj = datetime.strptime(time_str, "%H:%M")
            new_time = time_obj - timedelta(minutes=10)
            return new_time.strftime("%H:%M")
        except:
            return time_str

    def get_all_restaurants(self) -> List[Restaurant]:
        """Get all restaurants"""
        return self.db.query(Restaurant).filter(Restaurant.is_active == True).all()

    def populate_sample_restaurants(self) -> List[Restaurant]:
        """Populate database with sample restaurant data"""
        sample_restaurants = [
            {
                "name": "Swaad South Indian Kitchen",
                "address": "Colaba Causeway, Fort, Mumbai",
                "city": "Mumbai",
                "locality": "Colaba",
                "cuisine": "South Indian",
                "rating": 4.5,
                "total_capacity": 60,
                "phone": "+91 22 2202 0000",
                "email": "info@swaadkitchen.com"
            },
            {
                "name": "Punjab Grill",
                "address": "Phoenix Mills, Lower Parel, Mumbai",
                "city": "Mumbai",
                "locality": "Lower Parel",
                "cuisine": "North Indian",
                "rating": 4.7,
                "total_capacity": 80,
                "phone": "+91 22 6671 7666",
                "email": "reservations@punjabgrill.com"
            },
            {
                "name": "Trishna",
                "address": "7 Ropewalk Lane, Fort, Mumbai",
                "city": "Mumbai",
                "locality": "Fort",
                "cuisine": "Coastal Indian",
                "rating": 4.8,
                "total_capacity": 45,
                "phone": "+91 22 2270 3213",
                "email": "bookings@trishna.com"
            },
            {
                "name": "Mainland China",
                "address": "Linking Road, Bandra West, Mumbai",
                "city": "Mumbai",
                "locality": "Bandra West",
                "cuisine": "Chinese",
                "rating": 4.3,
                "total_capacity": 70,
                "phone": "+91 22 2640 3456",
                "email": "bandra@mainlandchina.co.in"
            },
            {
                "name": "The Bombay Canteen",
                "address": "Kamala Mills, Lower Parel, Mumbai",
                "city": "Mumbai",
                "locality": "Lower Parel",
                "cuisine": "Modern Indian",
                "rating": 4.6,
                "total_capacity": 90,
                "phone": "+91 22 4966 6666",
                "email": "hello@thebombaycanteen.com"
            },
            {
                "name": "Dakshin",
                "address": "Crowne Plaza, Adyar, Chennai",
                "city": "Chennai",
                "locality": "Adyar",
                "cuisine": "South Indian",
                "rating": 4.7,
                "total_capacity": 100,
                "phone": "+91 44 2499 4101",
                "email": "contact@dakshinchennai.com"
            },
            {
                "name": "Paragon Restaurant",
                "address": "M.G Road, Kochi",
                "city": "Kochi",
                "locality": "M.G Road",
                "cuisine": "Kerala Cuisine",
                "rating": 4.8,
                "total_capacity": 85,
                "phone": "+91 484 238 1432",
                "email": "info@paragonkochi.com"
            },
            {
                "name": "Truffles",
                "address": "Koramangala, Bangalore",
                "city": "Bangalore",
                "locality": "Koramangala",
                "cuisine": "Continental",
                "rating": 4.6,
                "total_capacity": 75,
                "phone": "+91 80 4146 6677",
                "email": "info@trufflesbangalore.com"
            },
            {
                "name": "Karim's",
                "address": "Jama Masjid, Old Delhi",
                "city": "Delhi",
                "locality": "Old Delhi",
                "cuisine": "Mughlai",
                "rating": 4.8,
                "total_capacity": 60,
                "phone": "+91 11 2326 4981",
                "email": "reservations@karimsdelhi.com"
            },
            {
                "name": "Bawarchi",
                "address": "RTC X Roads, Hyderabad",
                "city": "Hyderabad",
                "locality": "RTC X Roads",
                "cuisine": "Hyderabadi Biryani",
                "rating": 4.7,
                "total_capacity": 90,
                "phone": "+91 40 2763 9797",
                "email": "info@bawarchihyd.com"
            },
            {
                "name": "Copper Chimney",
                "address": "Alwarpet, Chennai",
                "city": "Chennai",
                "locality": "Alwarpet",
                "cuisine": "North Indian",
                "rating": 4.5,
                "total_capacity": 70,
                "phone": "+91 44 4231 4111",
                "email": "chennai@copperchimney.in"
            },
            {
                "name": "Kochi Kitchen",
                "address": "Marriott Hotel, Kochi",
                "city": "Kochi",
                "locality": "Marriott",
                "cuisine": "Seafood",
                "rating": 4.6,
                "total_capacity": 80,
                "phone": "+91 484 666 3333",
                "email": "reservations@kochikitchen.com"
            },
            {
                "name": "Airlines Hotel",
                "address": "Lavelle Road, Bangalore",
                "city": "Bangalore",
                "locality": "Lavelle Road",
                "cuisine": "South Indian",
                "rating": 4.4,
                "total_capacity": 60,
                "phone": "+91 80 2227 6291",
                "email": "info@airlinesbangalore.com"
            },
            {
                "name": "Dilli Haat",
                "address": "INA, Delhi",
                "city": "Delhi",
                "locality": "INA Market",
                "cuisine": "Street Food",
                "rating": 4.5,
                "total_capacity": 50,
                "phone": "+91 11 2611 0050",
                "email": "contact@dillihaat.com"
            },
            {
                "name": "Shah Ghouse",
                "address": "Tolichowki, Hyderabad",
                "city": "Hyderabad",
                "locality": "Tolichowki",
                "cuisine": "Hyderabadi Cuisine",
                "rating": 4.7,
                "total_capacity": 85,
                "phone": "+91 40 2356 7777",
                "email": "shahghouse@hyd.com"
            }
        ]

        created_restaurants = []
        for restaurant_data in sample_restaurants:
            restaurant = RestaurantCreate(**restaurant_data)
            db_restaurant = self.create_restaurant(restaurant)
            created_restaurants.append(db_restaurant)

        return created_restaurants
