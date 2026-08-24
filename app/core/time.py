"""
SENAContigo Timezone Management Utility.
Configures Colombia Standard Time (America/Bogota, UTC-5) across the backend.
"""
import os
import time
from datetime import datetime
from zoneinfo import ZoneInfo

COLOMBIA_TZ = ZoneInfo("America/Bogota")


def setup_colombia_timezone():
    """Set process-wide timezone environment variables to America/Bogota."""
    os.environ["TZ"] = "America/Bogota"
    try:
        time.tzset()
    except AttributeError:
        pass


def get_colombia_now() -> datetime:
    """Return the current datetime in Colombia Timezone (America/Bogota, UTC-5)."""
    return datetime.now(COLOMBIA_TZ)


def to_colombia_time(dt: datetime) -> datetime:
    """Convert any datetime (UTC or naive) to Colombia Timezone (America/Bogota, UTC-5)."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(COLOMBIA_TZ)
