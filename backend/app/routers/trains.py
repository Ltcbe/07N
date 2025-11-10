from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.db import get_db
from app.models.train import TrainRecord
from app.services.irail import fetch_irail_liveboard

router = APIRouter(prefix="/trains", tags=["Trains"])

def _as_dict(obj):
    return {
        "id": obj.id,
        "trainNumber": obj.train_number,
        "departureStation": obj.departure_station,
        "arrivalStation": obj.arrival_station,
        "scheduledTime": obj.scheduled_time.isoformat() if obj.scheduled_time else None,
        "actualTime": obj.actual_time.isoformat() if obj.actual_time else None,
        "delay": obj.delay,
        "status": obj.status,
        "source": obj.source,
        "createdAt": obj.created_at.isoformat() if obj.created_at else None,
    }

@router.get("/")
def get_trains(station: str, date: str, db: Session = Depends(get_db)):
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(400, detail="Format de date attendu: YYYY-MM-DD")

    existing = db.query(TrainRecord).filter(
        TrainRecord.departure_station == station,
        TrainRecord.scheduled_time >= date_obj,
        TrainRecord.scheduled_time < date_obj + timedelta(days=1)
    ).all()

    if existing:
        return [_as_dict(e) for e in existing]

    # Fetch from iRail, then persist
    trains = fetch_irail_liveboard(station)
    to_return = []
    for t in trains:
        record = TrainRecord(
            train_number=t["trainNumber"],
            departure_station=t["departureStation"],
            arrival_station=t["arrivalStation"],
            scheduled_time=t["scheduledTime"],
            actual_time=t["actualTime"],
            delay=t["delay"],
            status=t["status"],
            created_at=datetime.utcnow(),
        )
        db.add(record)
        to_return.append(_as_dict(record))
    db.commit()
    return to_return
