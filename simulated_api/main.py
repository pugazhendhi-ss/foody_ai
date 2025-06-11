from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from simulated_api.database.setup import Base, engine
from simulated_api.app.routers.restaurant_router import restaurant_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Restaurant Booking System API",
    description="A comprehensive restaurant search and booking system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(restaurant_router)



@app.get("/")
async def root():
    return {
        "message": "Restaurant Booking System API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "search_restaurants": "POST /api/v1/restaurants/search",
            "reserve_table": "POST /api/v1/restaurants/reserve",
            "create_restaurant": "POST /api/v1/restaurants",
            "get_restaurants": "GET /api/v1/restaurants",
            "populate_sample_data": "POST /api/v1/restaurants/populate"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# =============================================================================
# .env - Environment Variables
# =============================================================================

"""
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/restaurant_booking

# FastAPI Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
"""

# =============================================================================
# run.py - Application Runner
# =============================================================================

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=9000,
        reload=True,
        log_level="info"
    )

