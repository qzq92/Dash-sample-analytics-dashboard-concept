"""Pure parsing helpers for realtime weather payloads."""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional


def build_station_lookup(data: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build a station-id lookup from realtime weather payload metadata."""
    if not data or "data" not in data or "stations" not in data["data"]:
        return {}
    return {station["id"]: station for station in data["data"]["stations"]}


def normalize_unit(api_unit: Optional[str], default_unit: str) -> str:
    """Normalize API unit text with a default fallback."""
    if not api_unit:
        return default_unit
    return str(api_unit).replace("Degree Celsius", "°C").replace("Percentage", "%")


def convert_to_kmh(speed_val, speed_unit: str) -> Optional[float]:
    """Convert wind speed values to km/h when needed."""
    try:
        value = float(speed_val)
    except (TypeError, ValueError):
        return None
    if str(speed_unit).lower() in {"m/s", "metres per second", "meters per second"}:
        return value * 3.6
    return value


def is_within_singapore_bounds(lat: float, lon: float) -> bool:
    """Return whether coordinates are within broad Singapore bounds."""
    return 1.15 <= lat <= 1.50 and 103.55 <= lon <= 104.15


def is_within_last_5_minutes(datetime_str: str) -> bool:
    """Return whether an ISO datetime string is within the last five minutes."""
    if not datetime_str:
        return False
    try:
        reading_time = datetime.fromisoformat(datetime_str.replace("Z", "+00:00"))
        now = datetime.now(reading_time.tzinfo)
        return now - reading_time <= timedelta(minutes=5)
    except (ValueError, TypeError):
        return False
