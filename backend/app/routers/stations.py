from fastapi import APIRouter
from app.services.stations import fetch_all_stations

# --- Création du routeur FastAPI
router = APIRouter(
    prefix="/stations",
    tags=["Stations"]
)

@router.get("/")
def get_stations():
    """
    Retourne la liste complète des gares disponibles sur le réseau iRail (SNCB).
    Cette route interroge l'API publique https://api.irail.be/stations.
    Exemple : GET /stations
    """
    stations = fetch_all_stations()
    return stations
