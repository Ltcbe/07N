import requests
from datetime import datetime

def fetch_irail_connections(departure: str, arrival: str):
    """Interroge l'API iRail pour récupérer tous les trajets entre deux gares."""
    url = "https://api.irail.be/connections/"
    params = {
        "from": departure,
        "to": arrival,
        "format": "json",
        "lang": "fr",
    }
    r = requests.get(url, params=params, timeout=30, allow_redirects=True)
    r.raise_for_status()
    data = r.json()

    connections = []
    for c in data.get("connection", []):
        dep = c.get("departure", {})
        arr = c.get("arrival", {})
        connections.append({
            "trainNumber": dep.get("vehicle", "").split(".")[-1],
            "departureStation": dep.get("station"),
            "arrivalStation": arr.get("station"),
            "scheduledDeparture": datetime.fromtimestamp(int(dep.get("time", 0))),
            "scheduledArrival": datetime.fromtimestamp(int(arr.get("time", 0))),
            "delayDeparture": int(dep.get("delay", 0)) // 60,
            "delayArrival": int(arr.get("delay", 0)) // 60,
            "duration": c.get("duration"),
        })
    return connections
