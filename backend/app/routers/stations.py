from fastapi import APIRouter
from app.services.stations import fetch_all_stations

router = APIRouter(prefix="/stations", tags=["Stations"])

@router.get("/")
def get_stations():
    """
    Retourne la liste complète des gares disponibles sur iRail.
    """
    return fetch_all_stations()
