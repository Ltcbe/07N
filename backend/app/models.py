from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from sqlalchemy import String, Integer, Date, DateTime, Boolean, JSON, ForeignKey

class Base(DeclarativeBase):
    pass

class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[str] = mapped_column(String(64), index=True)
    date: Mapped[Date]
    delay_sec: Mapped[int] = mapped_column(Integer, default=0)
    last_stop_planned: Mapped[DateTime]
    last_stop_real: Mapped[DateTime | None]
    immutable_after: Mapped[DateTime]
    is_immutable: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[dict | None] = mapped_column(JSON)
    stops: Mapped[list["TripStop"]] = relationship(back_populates="trip", cascade="all, delete-orphan")

class TripStop(Base):
    __tablename__ = "trip_stops"
    id: Mapped[int] = mapped_column(primary_key=True)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id", ondelete="CASCADE"), index=True)
    stop_seq: Mapped[int]
    station_id: Mapped[str] = mapped_column(String(64))
    planned_arr: Mapped[DateTime | None]
    real_arr: Mapped[DateTime | None]
    arr_delay_sec: Mapped[int | None]
    planned_dep: Mapped[DateTime | None]
    real_dep: Mapped[DateTime | None]
    dep_delay_sec: Mapped[int | None]
    platform: Mapped[str | None] = mapped_column(String(16))
    canceled: Mapped[bool] = mapped_column(Boolean, default=False)
    raw_json: Mapped[dict | None] = mapped_column(JSON)
    trip: Mapped["Trip"] = relationship(back_populates="stops")
