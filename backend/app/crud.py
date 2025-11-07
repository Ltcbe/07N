from __future__ import annotations

from datetime import date, datetime
from typing import Dict, Iterable, List, Optional

from loguru import logger
from sqlalchemy.orm import Session

from .models import TrainJourney, TrainStop


def upsert_journey(session: Session, journey_payload: Dict) -> Optional[TrainJourney]:
    journey_id: str = journey_payload["id"]
    journey: Optional[TrainJourney] = session.get(TrainJourney, journey_id)

    finalization_time: Optional[datetime] = journey.finalization_time if journey else None
    if journey and finalization_time and datetime.utcnow() >= finalization_time:
        logger.debug("Skip update for finalized journey {journey_id}", journey_id=journey_id)
        return journey

    if journey is None:
        journey = TrainJourney(id=journey_id)
        session.add(journey)

    journey.vehicle = journey_payload.get("vehicle")
    journey.type = journey_payload.get("type")
    journey.number = journey_payload.get("number")
    journey.direction = journey_payload.get("direction")
    journey.departure_station = journey_payload.get("departure_station")
    journey.arrival_station = journey_payload.get("arrival_station")
    journey.trip_date = journey_payload.get("trip_date")
    journey.departure_time = journey_payload.get("departure_time")
    journey.arrival_time = journey_payload.get("arrival_time")
    journey.departure_delay = journey_payload.get("departure_delay") or 0
    journey.arrival_delay = journey_payload.get("arrival_delay") or 0
    journey.canceled = bool(journey_payload.get("canceled"))
    journey.left = bool(journey_payload.get("left"))
    journey.last_stop_time = journey_payload.get("last_stop_time")
    journey.finalization_time = journey_payload.get("finalization_time")
    journey.raw_payload = journey_payload.get("raw_payload")

    journey.stops.clear()
    stops_payload: Iterable[Dict] = journey_payload.get("stops", [])
    for stop_payload in stops_payload:
        stop = TrainStop(
            station=stop_payload.get("station"),
            time=stop_payload.get("time"),
            delay=stop_payload.get("delay") or 0,
            platform=stop_payload.get("platform"),
            status=stop_payload.get("status"),
            is_arrival=bool(stop_payload.get("is_arrival")),
            is_departure=bool(stop_payload.get("is_departure")),
            canceled=bool(stop_payload.get("canceled")),
            raw_payload=stop_payload.get("raw_payload"),
        )
        journey.stops.append(stop)

    return journey


def get_available_stations(session: Session) -> List[str]:
    stmt = session.query(TrainJourney.departure_station).distinct().order_by(TrainJourney.departure_station)
    return [row[0] for row in stmt.all() if row[0]]


def get_dashboard_data(
    session: Session,
    *,
    date: Optional[date] = None,
    departure_station: Optional[str] = None,
    arrival_station: Optional[str] = None,
) -> Dict:
    query = session.query(TrainJourney)
    if date:
        query = query.filter(TrainJourney.trip_date == date)
    if departure_station:
        query = query.filter(TrainJourney.departure_station == departure_station)
    if arrival_station:
        query = query.filter(TrainJourney.arrival_station == arrival_station)

    journeys: List[TrainJourney] = query.all()
    total = len(journeys)
    if total == 0:
        return {
            "summary": {
                "average_delay_minutes": 0,
                "late_trains": 0,
                "punctuality": 0,
            },
            "histogram": [],
            "journeys": [],
            "last_updated": None,
        }

    average_delay_minutes = sum(j.arrival_delay for j in journeys) / 60 / total
    late_trains = sum(1 for j in journeys if j.arrival_delay > 0 or j.departure_delay > 0)
    punctuality = ((total - late_trains) / total) * 100

    histogram = _build_histogram(journeys)
    journey_rows = [
        {
            "id": j.id,
            "train": j.number or j.vehicle,
            "type": j.type,
            "departure_station": j.departure_station,
            "arrival_station": j.arrival_station,
            "departure_time": j.departure_time.isoformat() if j.departure_time else None,
            "arrival_time": j.arrival_time.isoformat() if j.arrival_time else None,
            "delay_minutes": round((j.arrival_delay or j.departure_delay) / 60, 2),
            "status": _derive_status(j),
        }
        for j in journeys
    ]

    last_updated = max(j.updated_at for j in journeys if j.updated_at)

    return {
        "summary": {
            "average_delay_minutes": round(average_delay_minutes, 2),
            "late_trains": late_trains,
            "punctuality": round(punctuality, 2),
        },
        "histogram": histogram,
        "journeys": journey_rows,
        "last_updated": last_updated.isoformat() if last_updated else None,
    }


def _build_histogram(journeys: Iterable[TrainJourney]) -> List[Dict[str, int]]:
    buckets: Dict[int, int] = {hour: 0 for hour in range(24)}
    for journey in journeys:
        if not journey.departure_time:
            continue
        buckets[journey.departure_time.hour] += 1
    return [{"hour": hour, "count": buckets[hour]} for hour in range(24)]


def _derive_status(journey: TrainJourney) -> str:
    if journey.canceled:
        return "Annulé"
    delay = journey.arrival_delay or journey.departure_delay
    if delay >= 5 * 60:
        return "Retard"
    if delay > 0:
        return "Léger retard"
    return "À l'heure"
