from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from time import time
from app.routers import trains

app = FastAPI(title="iRail Backend with Persistence")

# --- Middleware CORS (pour le frontend Nginx)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


# --- Routes
app.include_router(trains.router)

@app.get("/health")
def health():
    return {"status": "ok"}
