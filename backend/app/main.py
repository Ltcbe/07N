from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import trains, stations, connections, network
from time import time

app = FastAPI(title="iRail Backend - Full Belgian Rail Network")

# --- CORS (à adapter selon ton domaine Dockploy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # autorise tout pour test
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Middleware de log des requêtes
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time()
    response = await call_next(request)
    process_time = (time() - start_time) * 1000
    print(f"{request.method} {request.url.path} → {response.status_code} ({process_time:.2f}ms)")
    return response


# --- Routers
app.include_router(trains.router)
app.include_router(stations.router)
app.include_router(connections.router)
app.include_router(network.router)


# --- Health check simple
@app.get("/health")
def health():
    return {"status": "ok"}
