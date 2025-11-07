import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
from datetime import datetime, date

DB_DSN = os.getenv("DB_DSN", "mariadb+mariadbconnector://irail:irailpwd@db:3306/irail")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173")
engine = create_engine(DB_DSN, pool_pre_ping=True)

app = FastAPI(title="SNCB Timing API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_date(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/metrics/summary")
def kpis(date: str, from_id: str|None=None, to_id: str|None=None):
    day = parse_date(date)
    where = ["date=:d"]
    params = {"d": day}
    if from_id:
        where.append("EXISTS (SELECT 1 FROM trip_stops s WHERE s.trip_id=t.id AND s.stop_seq=1 AND s.station_id=:from_id)")
        params["from_id"] = from_id
    if to_id:
        where.append("EXISTS (SELECT 1 FROM trip_stops s2 WHERE s2.trip_id=t.id AND s2.station_id=:to_id)")
        params["to_id"] = to_id
    sql = f"""SELECT
        COALESCE(AVG(t.delay_sec)/60,0) AS mean_delay_min,
        SUM(CASE WHEN t.delay_sec>60 THEN 1 ELSE 0 END) AS late_count,
        (100*SUM(CASE WHEN t.delay_sec<=60 THEN 1 ELSE 0 END)/NULLIF(COUNT(*),0)) AS punctual_rate
      FROM trips t WHERE {' AND '.join(where)}"""
    with Session(engine) as s:
        row = s.execute(text(sql), params).mappings().first()
        return {
            "meanDelay": float(row["mean_delay_min"] or 0),
            "lateCount": int(row["late_count"] or 0),
            "punctualRate": float(row["punctual_rate"] or 0),
        }

@app.get("/metrics/histogram")
def histogram(date: str, from_id: str|None=None, to_id: str|None=None):
    day = parse_date(date)
    where = ["date=:d"]
    params = {"d": day}
    # group by hour of last stop planned
    sql = f"""SELECT HOUR(last_stop_planned) AS h, COUNT(*) c
               FROM trips t WHERE date=:d GROUP BY HOUR(last_stop_planned) ORDER BY h"""
    with Session(engine) as s:
        rows = s.execute(text(sql), params).all()
        return [{"hour": int(h), "trips": int(c)} for (h,c) in rows]

@app.get("/trips")
def trips(date: str, page:int=1, size:int=100):
    day = parse_date(date)
    offset = (page-1)*size
    sql = text("""SELECT t.id, t.vehicle_id, t.delay_sec, t.last_stop_planned, t.last_stop_real,
                    (SELECT s1.station_id FROM trip_stops s1 WHERE s1.trip_id=t.id ORDER BY s1.stop_seq ASC LIMIT 1) AS from_station,
                    (SELECT s2.station_id FROM trip_stops s2 WHERE s2.trip_id=t.id ORDER BY s2.stop_seq DESC LIMIT 1) AS to_station
                  FROM trips t WHERE t.date=:d ORDER BY t.last_stop_planned LIMIT :size OFFSET :offset""")
    count_sql = text("SELECT COUNT(*) FROM trips WHERE date=:d")
    with Session(engine) as s:
        items = [dict(r._mapping) for r in s.execute(sql, {"d":day,"size":size,"offset":offset}).all()]
        total = s.execute(count_sql, {"d":day}).scalar_one()
        return {"total": int(total), "items": items}
