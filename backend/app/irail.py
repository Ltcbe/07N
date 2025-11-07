from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

import httpx
from dateutil import tz
from loguru import logger

from .config import get_settings

API_BASE_URL = "https://api.irail.be"

settings = get_settings()


class IRailClient:
    def __init__(self, timeout: int = 30) -> None:
        self._client = httpx.AsyncClient(base_url=API_BASE_URL, timeout=timeout)
        self._timezone = tz.gettz("Europe/Brussels")

    async def close(self) -> None:
        await self._client.aclose()

    async def fetch_liveboard(self, station: str) -> List[Dict[str, Any]]:
        params = {
            "station": station,
            "format": "json",
            "fast": "true",
            "alerts": "false",
        }
        response = await self._client.get("/liveboard/", params=params)
        response.raise_for_status()
        payload = response.json()
        departures = payload.get("departures", {}).get("departure", [])
        if isinstance(departures, dict):
            departures = [departures]
        return departures

    async def fetch_vehicle(self, vehicle_id: str) -> Dict[str, Any]:
        params = {"id": vehicle_id, "format": "json"}
        response = await self._client.get("/vehicle/", params=params)
        response.raise_for_status()
        return response.json()

    async def fetch_stationboard(self, station: str) -> List[Dict[str, Any]]:
        try:
            return await self.fetch_liveboard(station)
        except httpx.HTTPError as exc:
            logger.error("Failed to fetch liveboard for {station}: {error}", station=station, error=str(exc))
            return []

    async def fetch_full_journeys(self, station: str) -> List[Dict[str, Any]]:
        departures = await self.fetch_stationboard(station)
        tasks = []
        for departure in departures:
            vehicle_id = departure.get("vehicle")
            if not vehicle_id:
                continue
            tasks.append(self.fetch_vehicle(vehicle_id))
        journeys: List[Dict[str, Any]] = []
        for chunk in _batched(tasks, 4):
            results = await asyncio.gather(*chunk, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logger.warning("Vehicle fetch failed: {error}", error=str(result))
                    continue
                journeys.append(result)
        return journeys


def _batched(iterable: Iterable[Any], n: int) -> Iterable[Tuple[Any, ...]]:
    batch: List[Any] = []
    for item in iterable:
        batch.append(item)
        if len(batch) == n:
            yield tuple(batch)
            batch.clear()
    if batch:
        yield tuple(batch)


def parse_journey(vehicle_payload: Dict[str, Any], departure_station: Optional[str] = None) -> Optional[Dict[str, Any]]:
    vehicle_info = vehicle_payload.get("vehicleinfo", {})
    stops_info = vehicle_payload.get("stops", {})
    stops_raw = stops_info.get("stop", [])
    if isinstance(stops_raw, dict):
        stops_raw = [stops_raw]
    if not stops_raw:
        return None

    stops: List[Dict[str, Any]] = []
    departure_time: Optional[datetime] = None
    arrival_time: Optional[datetime] = None
    departure_delay = 0
    arrival_delay = 0
    arrival_station = None

    for stop in stops_raw:
        station_name = stop.get("station")
        time_epoch = _parse_int(stop.get("time"))
        delay = _parse_int(stop.get("delay"))
        platform = _extract_platform(stop.get("platform"))
        status = stop.get("status")
        canceled = stop.get("canceled") == "1"
        is_arrival = stop.get("arrived") == "1"
        is_departure = stop.get("left") == "1"

        dt = _epoch_to_datetime(time_epoch)
        stops.append(
            {
                "station": station_name,
                "time": dt,
                "delay": delay,
                "platform": platform,
                "status": status,
                "is_arrival": is_arrival,
                "is_departure": is_departure,
                "canceled": canceled,
                "raw_payload": stop,
            }
        )
        if not departure_time and (departure_station is None or station_name == departure_station):
            departure_time = dt
            departure_delay = delay
        arrival_time = dt
        arrival_delay = delay
        arrival_station = station_name

    journey_id = vehicle_payload.get("vehicle")
    if not journey_id:
        return None

    trip_date = departure_time.date() if departure_time else datetime.utcnow().date()
    finalization_time = (arrival_time + timedelta(minutes=5)) if arrival_time else None

    payload = {
        "id": f"{journey_id}_{int(departure_time.timestamp()) if departure_time else ''}",
        "vehicle": journey_id,
        "type": vehicle_info.get("type"),
        "number": vehicle_info.get("number"),
        "direction": vehicle_info.get("direction"),
        "departure_station": departure_station or stops[0]["station"],
        "arrival_station": arrival_station,
        "trip_date": trip_date,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
        "departure_delay": departure_delay,
        "arrival_delay": arrival_delay,
        "canceled": vehicle_info.get("canceled", "0") == "1",
        "left": vehicle_info.get("left", "0") == "1",
        "last_stop_time": arrival_time,
        "finalization_time": finalization_time,
        "stops": stops,
        "raw_payload": {
            key: value for key, value in vehicle_payload.items() if key != "connections"
        },
    }
    return payload


def _parse_int(value: Optional[Any]) -> Optional[int]:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _epoch_to_datetime(value: Optional[int]) -> Optional[datetime]:
    if value is None:
        return None
    return datetime.fromtimestamp(value, tz=tz.UTC).astimezone(tz=tz.gettz("Europe/Brussels")).replace(tzinfo=None)


def _extract_platform(platform_data: Any) -> Optional[str]:
    if isinstance(platform_data, dict):
        text = platform_data.get("#text")
        if text:
            return str(text)
    elif platform_data is not None:
        return str(platform_data)
    return None
