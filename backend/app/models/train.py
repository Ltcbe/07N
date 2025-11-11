from sqlalchemy import Column, Integer, String, DateTime, Float
from app.db import Base
from datetime import datetime
from pydantic import BaseModel

# --- Modèle SQLAlchemy (table train_records)
class TrainRecord(Base):
    __tablename__ = "train_records"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(50), index=True)
    departure_station = Column(String(100), index=True)
    arrival_station = Column(String(100), index=True)
    scheduled_time = Column(DateTime)
    actual_time = Column(DateTime)
    delay = Column(Float)
    status = Column(String(20))
    source = Column(String(20), default="irail")
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Modèle Pydantic (pour le JSON de sortie)
class TrainRecordOut(BaseModel):
    id: int
    train_number: str | None = None
    departure_station: str
    arrival_station: str
    scheduled_time: datetime | None = None
    actual_time: datetime | None = None
    delay: float | None = None
    status: str | None = None
    source: str | None = None
    created_at: datetime | None = None

    class Config:
        orm_mode = True
