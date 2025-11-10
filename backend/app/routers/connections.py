from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.services.connections import fetch_irail_connections
from app.models.train import TrainRecord
from datetime import datetime

router = APIRouter(prefix="/connections", tags=["Connections"])

@router.get("")
def get_connections(from_station: str, to_station: str, db: Session = Depends(get_db)):
    """
    Retourne tous les trajets entre deux gares belges.
    Exemple : /connections?from_station=Brussels-Central&to_station=Gent-Sint-Pieters
    """
    if not from_station or not to_station:
        raise HTTPException(400, detail="Les deux gares doivent être précisées.")

    try:
        results = fetch_irail_connections(from_station, to_station)
    except Exception as e:
        raise HTTPException(500, detail=f"Erreur iRail: {e}")

    # Sauvegarde chaque connexion en DB pour analyse ultérieure
    for t in results:
        record = TrainRecord(
            train_number=t["trainNumber"],
            departure_station=t["departureStation"],
            arrival_station=t["arrivalStation"],
            scheduled_time=t["scheduledDeparture"],
            actual_time=t["scheduledArrival"],
            delay=t["delayArrival"],
            status="delayed" if t["delayArrival"] > 0 else "on-time",
            created_at=datetime.utcnow(),
        )
        db.add(record)
    db.commit()

    return results
