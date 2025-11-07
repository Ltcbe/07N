from datetime import datetime

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .database import Base


class TrainJourney(Base):
    __tablename__ = "train_journeys"

    id = Column(String, primary_key=True, index=True)
    vehicle = Column(String, index=True, nullable=False)
    type = Column(String, nullable=True)
    number = Column(String, nullable=True)
    direction = Column(String, nullable=True)

    departure_station = Column(String, index=True, nullable=False)
    arrival_station = Column(String, nullable=True)

    trip_date = Column(Date, index=True, nullable=False)

    departure_time = Column(DateTime(timezone=False), nullable=False)
    arrival_time = Column(DateTime(timezone=False), nullable=True)

    departure_delay = Column(Integer, default=0)
    arrival_delay = Column(Integer, default=0)

    canceled = Column(Boolean, default=False)
    left = Column(Boolean, default=False)

    last_stop_time = Column(DateTime(timezone=False), nullable=True)
    finalization_time = Column(DateTime(timezone=False), nullable=True)

    raw_payload = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow)

    stops = relationship("TrainStop", back_populates="journey", cascade="all, delete-orphan")


class TrainStop(Base):
    __tablename__ = "train_stops"

    id = Column(Integer, primary_key=True, autoincrement=True)
    journey_id = Column(String, ForeignKey("train_journeys.id", ondelete="CASCADE"), index=True)

    station = Column(String, nullable=False)
    time = Column(DateTime(timezone=False), nullable=True)
    delay = Column(Integer, default=0)
    platform = Column(String, nullable=True)
    status = Column(String, nullable=True)
    is_arrival = Column(Boolean, default=False)
    is_departure = Column(Boolean, default=False)
    canceled = Column(Boolean, default=False)

    raw_payload = Column(JSON, nullable=False)

    journey = relationship("TrainJourney", back_populates="stops")
