from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import trains

app = FastAPI(title="iRail Backend with Persistence")

# CORS not strictly needed behind Nginx proxy, but harmless
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trains.router)

@app.get("/health")
def health():
    return {"status": "ok"}
