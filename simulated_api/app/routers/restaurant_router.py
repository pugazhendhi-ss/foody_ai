from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from simulated_api.app.models.pydantics import (
    RestaurantCreate, RestaurantResponse, RestaurantSearchRequest,
    RestaurantSearchResponse, ReservationRequest, ReservationErrorResponse
)
from simulated_api.app.services.restaurant_manager import RestaurantManager
from simulated_api.database.setup import get_db

restaurant_router = APIRouter(prefix="/api/v1", tags=["restaurants"])


@restaurant_router.post("/restaurants", response_model=RestaurantResponse)
async def create_restaurant(
        restaurant: RestaurantCreate,
        db: Session = Depends(get_db)
):
    """Create a new restaurant"""
    try:
        manager = RestaurantManager(db)
        db_restaurant = manager.create_restaurant(restaurant)
        return db_restaurant
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Server error", "details": str(e)}
        )


@restaurant_router.get("/restaurants", response_model=List[RestaurantResponse])
async def get_restaurants(db: Session = Depends(get_db)):
    """Get all restaurants"""
    try:
        manager = RestaurantManager(db)
        restaurants = manager.get_all_restaurants()
        return restaurants
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Server error", "details": str(e)}
        )


@restaurant_router.post("/restaurants/search", response_model=List[RestaurantSearchResponse])
async def search_restaurants(
        search_params: RestaurantSearchRequest,
        db: Session = Depends(get_db)
):
    """Search restaurants based on criteria"""
    try:
        manager = RestaurantManager(db)
        restaurants = manager.search_restaurants(search_params)

        if not restaurants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"restaurants": []}
            )
        return restaurants

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad request", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Server error", "details": str(e)}
        )


@restaurant_router.post("/restaurants/reserve")
async def reserve_table(
        reservation: ReservationRequest,
        db: Session = Depends(get_db)
):
    """Reserve a table at a restaurant"""
    try:
        manager = RestaurantManager(db)
        result = manager.reserve_table(reservation)

        if isinstance(result, ReservationErrorResponse):
            if result.status == "invalid_restaurant":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result.model_dump()
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=result.model_dump()
                )
        return result

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Bad request", "details": str(e)}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Server error", "details": str(e)}
        )


@restaurant_router.post("/restaurants/populate", response_model=List[RestaurantResponse])
async def populate_restaurants(db: Session = Depends(get_db)):
    """Populate database with sample restaurants"""
    try:
        manager = RestaurantManager(db)
        restaurants = manager.populate_sample_restaurants()
        return restaurants
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Server error", "details": str(e)}
        )

