from __future__ import annotations

import asyncio
import contextlib
import sys
from datetime import date
from typing import Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .config import get_settings
from .crud import get_dashboard_data
from .database import get_db
from .prestart import init_db
from .services import fetch_and_store_once, get_known_stations, scheduler_loop

settings = get_settings()

logger.remove()
logger.add(sys.stdout, level=settings.log_level.upper())

app = FastAPI(title="SNCB Timing Dashboard", version="1.0.0")

_scheduler_task: Optional[asyncio.Task] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event() -> None:
    global _scheduler_task
    logger.info("Application startup")
    init_db()
    _scheduler_task = asyncio.create_task(scheduler_loop())


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global _scheduler_task
    if _scheduler_task:
        _scheduler_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await _scheduler_task
        _scheduler_task = None


@app.get("/health")
def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/api/fetch")
async def trigger_fetch() -> dict:
    processed = await fetch_and_store_once()
    return {"processed": processed}


@app.get("/api/stations")
def list_stations():
    return {"stations": get_known_stations()}


@app.get("/api/dashboard")
def get_dashboard(
    day: Optional[date] = Query(default=None),
    departure_station: Optional[str] = Query(default=None),
    arrival_station: Optional[str] = Query(default=None),
):
    with get_db() as session:
        data = get_dashboard_data(
            session,
            date=day,
            departure_station=departure_station,
            arrival_station=arrival_station,
        )
    return data
