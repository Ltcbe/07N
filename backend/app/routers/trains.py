from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.train import TrainRecord, TrainRecordOut
from typing import List

router = APIRouter(prefix="/trains", tags=["Trains"])


@router.get("/", response_model=List[TrainRecordOut])
def list_trains(db: Session = Depends(get_db)):
    """
    Liste complète des trains enregistrés.
    """
    return db.query(TrainRecord).order_by(TrainRecord.scheduled_time.desc()).limit(100).all()


@router.get("/search", response_model=List[TrainRecordOut])
def search_trains(
    from_station: str = Query(..., alias="from", description="Nom de la gare de départ"),
    to_station: str = Query(..., alias="to", description="Nom de la gare d'arrivée"),
    db: Session = Depends(get_db),
):
    """
    Recherche les trajets selon la gare de départ et la gare d'arrivée.

    Exemple:
      /trains/search?from=Brussels-Central&to=Liège-Guillemins
    """
    query = (
        db.query(TrainRecord)
        .filter(TrainRecord.departure_station == from_station)
        .filter(TrainRecord.arrival_station == to_station)
        .order_by(TrainRecord.scheduled_time)
    )

    results = query.all()
    return results
