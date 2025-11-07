from __future__ import annotations

import asyncio
from datetime import datetime
from typing import List

from loguru import logger

from .config import get_settings
from .crud import get_available_stations, upsert_journey
from .database import get_db
from .irail import IRailClient, parse_journey

settings = get_settings()


async def fetch_and_store_once() -> int:
    client = IRailClient()
    inserted = 0
    try:
        for station in settings.stations:
            logger.info("Fetching journeys for station {station}", station=station)
            journeys_payloads = await client.fetch_full_journeys(station)
            for vehicle_payload in journeys_payloads:
                journey_payload = parse_journey(vehicle_payload, departure_station=station)
                if not journey_payload:
                    continue
                inserted += _store_journey(journey_payload)
    finally:
        await client.close()
    return inserted


def _store_journey(journey_payload) -> int:
    from sqlalchemy.exc import SQLAlchemyError

    with get_db() as session:
        try:
            upsert_journey(session, journey_payload)
            return 1
        except SQLAlchemyError as exc:
            session.rollback()
            logger.error("Failed to store journey {id}: {error}", id=journey_payload.get("id"), error=str(exc))
            return 0


async def scheduler_loop() -> None:
    interval = max(60, settings.fetch_interval_seconds)
    logger.info("Starting fetch scheduler with interval {interval}s", interval=interval)
    while True:
        start_time = datetime.utcnow()
        try:
            inserted = await fetch_and_store_once()
            logger.info("Fetch cycle completed: {count} journeys processed", count=inserted)
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Fetch cycle failed: {error}", error=str(exc))
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        await asyncio.sleep(max(5, interval - int(elapsed)))


def get_known_stations() -> List[str]:
    with get_db() as session:
        stations = get_available_stations(session)
    if stations:
        return stations
    return settings.stations
