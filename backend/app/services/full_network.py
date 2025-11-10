import requests

def collect_full_network():
    """
    Récupère la liste de toutes les connexions ferroviaires belges depuis iRail.
    (Cette version simplifiée ne fait qu'un test de disponibilité.)
    """
    try:
        res = requests.get("https://api.irail.be/stations/?format=json", timeout=10)
        res.raise_for_status()
        data = res.json()
        stations = [s["name"] for s in data.get("station", [])]
        return {"total_stations": len(stations), "stations": stations}
    except Exception as e:
        return {"error": str(e)}
