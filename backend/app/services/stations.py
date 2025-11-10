import requests

def fetch_all_stations():
    """
    Récupère la liste complète des gares depuis l'API iRail.
    Retourne un tableau de noms de gares.
    """
    url = "https://api.irail.be/stations/?format=json&lang=fr"
    r = requests.get(url, allow_redirects=True, timeout=20)
    r.raise_for_status()
    data = r.json()
    stations = [s["name"] for s in data.get("station", []) if "name" in s]
    return sorted(set(stations))
