# backend/app/routers/connections.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.train import TrainRecord
from app.services.irail import fetch_irail_liveboard

router = APIRouter(prefix="/connections", tags=["Connections"])

@router.get("/")
def list_connections(db: Session = Depends(get_db)):
    """Retourne la liste des connexions ferroviaires enregistrées"""
    connections = db.query(TrainRecord).limit(100).all()
    return connections

@router.get("/station/{station_name}")
def get_connections_for_station(station_name: str, db: Session = Depends(get_db)):
    """Retourne les trajets depuis une gare donnée"""
    trains = db.query(TrainRecord).filter(
        TrainRecord.departure_station == station_name
    ).all()
    if not trains:
        raise HTTPException(status_code=404, detail="Aucune connexion trouvée pour cette gare.")
    return trains
