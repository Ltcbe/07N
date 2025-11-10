import requests
from datetime import datetime

def fetch_irail_liveboard(station_name: str):
    base_url = "https://api.irail.be/liveboard/"
    params = {
        "station": station_name,
        "arrdep": "departure",
        "format": "json",
        "lang": "fr"
    }

    r = requests.get(base_url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    trains = []
    for dep in data.get("departures", {}).get("departure", []):
        delay = int(dep.get("delay", 0) or 0)
        status = "cancelled" if dep.get("canceled") == "1" else ("delayed" if delay > 0 else "on-time")
        trains.append({
            "trainNumber": dep.get("vehicle", "").split(".")[-1],
            "departureStation": data["station"],
            "arrivalStation": dep.get("station"),
            "scheduledTime": datetime.fromtimestamp(int(dep["time"])),
            "actualTime": datetime.fromtimestamp(int(dep["time"]) + delay),
            "delay": round(delay / 60, 1),
            "status": status,
        })
    return trains
