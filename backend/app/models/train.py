from sqlalchemy import Column, Integer, String, DateTime, Float, Index
from app.db import Base

class TrainRecord(Base):
    __tablename__ = "train_records"

    id = Column(Integer, primary_key=True, index=True)
    train_number = Column(String(50), index=True)
    departure_station = Column(String(100), index=True)
    arrival_station = Column(String(100), index=True)
    scheduled_time = Column(DateTime)
    actual_time = Column(DateTime)
    delay = Column(Float)
    status = Column(String(20))  # on-time, delayed, cancelled
    source = Column(String(20), default="irail")
    created_at = Column(DateTime)

Index("ix_train_day_station", TrainRecord.departure_station, TrainRecord.scheduled_time)
