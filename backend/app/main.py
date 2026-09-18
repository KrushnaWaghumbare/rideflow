from fastapi import FastAPI

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.db_health import router as db_health_router
from app.api.routes.users import router as users_router
from app.api.routes.drivers import router as drivers_router
from app.api.routes.vehicles import router as vehicles_router
from app.api.routes import rides
app = FastAPI(
    title=settings.app_name,
    description="Cab Booking System API",
    version=settings.app_version
)


@app.get("/")
def root():
    return {
        "message": "Welcome to RideFlow API"
    }


app.include_router(health_router)
app.include_router(db_health_router)
app.include_router(users_router)
app.include_router(drivers_router)
app.include_router(vehicles_router)
app.include_router(
    rides.router,
    prefix="/rides",
    tags=["Rides"]
)