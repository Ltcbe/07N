import os, asyncio, httpx
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.utils import to_dt

DB_DSN = os.getenv("DB_DSN", "mariadb+mariadbconnector://irail:irailpwd@db:3306/irail")
IRAIL = os.getenv("IRAIL_BASE", "https://api.irail.be")
RATE = int(os.getenv("RATE_LIMIT_RPM", "60"))

engine = create_engine(DB_DSN, pool_pre_ping=True)

def compute_immutable_after(stops):
    # base = dernière heure réelle sinon prévue
    real_times = [to_dt(s.get('time', {}).get('arrival', {}).get('realtime')) or to_dt(s.get('time', {}).get('departure', {}).get('realtime')) for s in stops]
    planned_times = [to_dt(s.get('time', {}).get('arrival', {}).get('scheduled')) or to_dt(s.get('time', {}).get('departure', {}).get('scheduled')) for s in stops]
    base = max([t for t in real_times if t] or [None], default=None) or max([t for t in planned_times if t] or [None], default=None)
    if base is None:
        base = datetime.now(timezone.utc)
    return base + timedelta(minutes=5)

async def fetch_json(client, url, params):
    for attempt in range(5):
        r = await client.get(url, params=params, timeout=20, headers={"User-Agent": "irail-dashboard/1.0"})
        if r.status_code == 429 or r.status_code >= 500:
            await asyncio.sleep(2**attempt)
            continue
        r.raise_for_status()
        return r.json()
    raise RuntimeError("Too many retries")

def upsert_trip_and_stops(vehicle_json: dict):
    # vehicle_json is per iRail /vehicle response
    vehicle_id = vehicle_json.get("vehicle", {}).get("name") or vehicle_json.get("id") or vehicle_json.get("vehicle")
    stops = vehicle_json.get("stops", {}).get("stop", [])
    if not vehicle_id or not stops:
        return
    # date is day of first stop planned
    dt_first = to_dt(stops[0].get("time", {}).get("departure", {}).get("scheduled") or stops[0].get("time", {}).get("arrival", {}).get("scheduled"))
    trip_date = (dt_first or datetime.now(timezone.utc)).date()
    immutable_after = compute_immutable_after(stops)

    # delay: difference arrival final scheduled vs realtime (seconds)
    last = stops[-1]
    sched = to_dt(last.get("time", {}).get("arrival", {}).get("scheduled") or last.get("time", {}).get("departure", {}).get("scheduled"))
    real = to_dt(last.get("time", {}).get("arrival", {}).get("realtime") or last.get("time", {}).get("departure", {}).get("realtime")) or sched
    delay_sec = int((real - sched).total_seconds()) if sched and real else 0

    last_planned = max([to_dt(s.get("time", {}).get("arrival", {}).get("scheduled")) or to_dt(s.get("time", {}).get("departure", {}).get("scheduled")) for s in stops if s], default=None)
    last_real = max([to_dt(s.get("time", {}).get("arrival", {}).get("realtime")) or to_dt(s.get("time", {}).get("departure", {}).get("realtime")) for s in stops if s], default=None)

    with Session(engine) as s:
        # insert or ignore trip
        s.execute(text("""INSERT INTO trips (vehicle_id, date, delay_sec, last_stop_planned, last_stop_real, immutable_after, raw_json)
                          VALUES (:vid, :d, :delay, :lsp, :lsr, :imm, :raw)
                          ON DUPLICATE KEY UPDATE
                            delay_sec=IF(NOW() < immutable_after, VALUES(delay_sec), delay_sec),
                            last_stop_real=IF(NOW() < immutable_after, VALUES(last_stop_real), last_stop_real),
                            raw_json=IF(NOW() < immutable_after, VALUES(raw_json), raw_json)
                       """),
                 {"vid": vehicle_id, "d": trip_date, "delay": delay_sec,
                  "lsp": (last_planned or real).replace(tzinfo=None),
                  "lsr": (last_real.replace(tzinfo=None) if last_real else None),
                  "imm": immutable_after.replace(tzinfo=None),
                  "raw": vehicle_json})
        # get id
        trip_id = s.execute(text("SELECT id FROM trips WHERE vehicle_id=:v AND date=:d"), {"v": vehicle_id, "d": trip_date}).scalar_one()

        # delete and reinsert stops only if before immutability
        ok = s.execute(text("SELECT NOW() < immutable_after FROM trips WHERE id=:id"), {"id": trip_id}).scalar_one()
        if ok:
            s.execute(text("DELETE FROM trip_stops WHERE trip_id=:id"), {"id": trip_id})
            for i, stop in enumerate(stops, start=1):
                arr_s = stop.get("time", {}).get("arrival", {})
                dep_s = stop.get("time", {}).get("departure", {})
                def to_naive(ts): 
                    d = to_dt(ts); 
                    return d.replace(tzinfo=None) if d else None
                s.execute(text("""INSERT INTO trip_stops
                    (trip_id, stop_seq, station_id, planned_arr, real_arr, arr_delay_sec,
                     planned_dep, real_dep, dep_delay_sec, platform, canceled, raw_json)
                    VALUES (:trip_id, :seq, :station, :pa, :ra, :arrd, :pd, :rd, :depd, :platform, :canceled, :raw)
                """), {
                    "trip_id": trip_id,
                    "seq": i,
                    "station": stop.get("stationinfo", {}).get("id") or stop.get("station"),
                    "pa": to_naive(arr_s.get("scheduled")),
                    "ra": to_naive(arr_s.get("realtime")),
                    "arrd": int(arr_s.get("delay", 0) or 0) if isinstance(arr_s.get("delay", 0), int) else 0,
                    "pd": to_naive(dep_s.get("scheduled")),
                    "rd": to_naive(dep_s.get("realtime")),
                    "depd": int(dep_s.get("delay", 0) or 0) if isinstance(dep_s.get("delay", 0), int) else 0,
                    "platform": stop.get("platform"),
                    "canceled": bool(stop.get("canceled", False)),
                    "raw": stop
                })
        s.commit()

def mark_immutable():
    with Session(engine) as s:
        s.execute(text("UPDATE trips SET is_immutable=TRUE WHERE NOW() >= immutable_after AND is_immutable=FALSE"))
        s.commit()

async def ingest_once():
    async with httpx.AsyncClient() as client:
        # stations list
        st = await fetch_json(client, f"{IRAIL}/stations", {"format":"json"})
        stations = st.get("station", [])
        for s in stations:
            sid = s.get("id")
            if not sid: 
                continue
            lb = await fetch_json(client, f"{IRAIL}/liveboard", {"id": sid, "format":"json"})
            deps = (lb.get("departures", {}) or {}).get("departure", [])
            for d in deps:
                vehicle = d.get("vehicle")
                if not vehicle:
                    continue
                v = await fetch_json(client, f"{IRAIL}/vehicle", {"id": vehicle, "format":"json"})
                upsert_trip_and_stops(v)
        mark_immutable()

async def main():
    while True:
        try:
            await ingest_once()
        except Exception as e:
            print("Ingestion error:", e)
        await asyncio.sleep(120)  # every 2 minutes

if __name__ == "__main__":
    asyncio.run(main())
