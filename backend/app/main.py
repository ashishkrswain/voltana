from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, engine
from app.routers import vehicles, chargers, trip, trips, tools
from app.models import Vehicle, Charger, ChargerNetwork, SavedTrip


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Voltana API",
    description="Unified India EV Route & Charging Planner API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles.router)
app.include_router(chargers.router)
app.include_router(trip.router)
app.include_router(trips.router)
app.include_router(tools.router)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "voltana"}