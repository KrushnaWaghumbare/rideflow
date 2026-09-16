from fastapi import FastAPI

app = FastAPI(
    title="RideFlow API",
    description="Cab Booking System API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {
        "message": "Welcome to RideFlow API"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }