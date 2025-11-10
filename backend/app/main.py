from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from time import time
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.routers import trains, stations
from app.services.collector import collect_all_trains

# --- Application FastAPI
app = FastAPI(title="iRail Backend with Persistence and Scheduler")

# --- Middleware CORS pour autoriser le frontend (ex: http://localhost:8081)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou ["http://localhost:8081"] en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Middleware de log HTTP
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time()
    client_ip = request.client.host if request.client else "?"
    method = request.method
    path = request.url.path
    query = request.url.query

    print(f"➡️  {client_ip} → {method} {path}?{query}")
    try:
        response = await call_next(request)
    except Exception as e:
        process_time = (time() - start_time) * 1000
        print(f"💥  {method} {path} ERREUR {e} ({process_time:.2f} ms)")
        raise e

    process_time = (time() - start_time) * 1000
    print(f"⬅️  {method} {path} → {response.status_code} ({process_time:.2f} ms)")
    return response


# --- Fonction de collecte automatique (toutes les gares)
def start_collector():
    db: Session = SessionLocal()
    try:
        collect_all_trains(db)
    finally:
        db.close()


# --- Planificateur automatique
scheduler = BackgroundScheduler()
scheduler.add_job(start_collector, "interval", hours=1, id="irail_collector")
scheduler.start()

print("⏱️  Collecteur iRail planifié (toutes les 1h)")

# --- Routes API
app.include_router(trains.router)
app.include_router(stations.router)

@app.get("/health")
def health():
    return {"status": "ok"}
