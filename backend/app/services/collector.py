from datetime import datetime
from sqlalchemy.orm import Session
from app.services.irail import fetch_irail_liveboard
from app.services.stations import fetch_all_stations
from app.models.train import TrainRecord
import time

def collect_all_trains(db: Session):
    stations = fetch_all_stations()
    date_today = datetime.now().strftime("%Y-%m-%d")
    print(f"🚆 Début de la collecte pour {len(stations)} gares ({date_today})")

    for station in stations:
        try:
            trains = fetch_irail_liveboard(station)
            for t in trains:
                record = TrainRecord(
                    train_number=t["trainNumber"],
                    departure_station=t["departureStation"],
                    arrival_station=t["arrivalStation"],
                    scheduled_time=t["scheduledTime"],
                    actual_time=t["actualTime"],
                    delay=t["delay"],
                    status=t["status"],
                    created_at=datetime.utcnow()
                )
                db.add(record)
            db.commit()
            print(f"✅ {station}: {len(trains)} trajets collectés")
        except Exception as e:
            print(f"⚠️ Erreur iRail pour {station}: {e}")
        time.sleep(0.5)  # ⏳ anti flood iRail
