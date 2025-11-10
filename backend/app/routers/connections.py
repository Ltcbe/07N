from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from time import time
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.routers import trains, stations, connections, network
from app.services.collector import collect_all_trains
from app.services.full_network import collect_full_network


# --- Application FastAPI
app = FastAPI(title="iRail Backend - Full Belgian Rail Network")

# --- Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # tu peux restreindre à ["https://time.terminalcommun.be", "http://localhost:5173"]
    ],
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


# --- Collecte horaire des trains en direct (toutes les gares principales)
def start_collector():
    db: Session = SessionLocal()
    try:
        collect_all_trains(db)
    finally:
        db.close()


# --- Collecte complète du réseau ferroviaire (toutes les gares, toutes les connexions)
def start_network_collector():
    db: Session = SessionLocal()
    try:
        collect_full_network(db)
    finally:
        db.close()


# --- Planificateur automatique
scheduler = BackgroundScheduler()

# Collecte partielle (liveboard)
scheduler.add_job(start_collector, "interval", hours=1, id="irail_collector")

# Collecte complète du réseau (tous les trajets)
scheduler.add_job(start_network_collector, "cron", hour="3", id="full_network_collector")

scheduler.start()
print("⏱️  Collecteur iRail planifié (liveboard toutes les 1h, réseau complet à 3h du matin)")


# --- Routes API
app.include_router(trains.router)
app.include_router(stations.router)
app.include_router(connections.router)
app.include_router(network.router)


# --- Route de santé
@app.get("/health")
def health():
    return {"status": "ok"}
