from datetime import datetime, timezone

def to_dt(ts: str | int | None) -> datetime | None:
    if ts is None:
        return None
    # iRail gives epoch seconds as strings
    try:
        v = int(ts)
        return datetime.fromtimestamp(v, tz=timezone.utc)
    except Exception:
        return None
