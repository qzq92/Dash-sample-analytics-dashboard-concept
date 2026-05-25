"""ERP gantry data helpers."""

import re
from typing import Any, Dict, List

from utils.data_download_helper import fetch_erp_gantry_data
from utils.transport.cache import _road_infra_cache


def extract_gantry_number(description: str) -> str:
    """Extract ERP gantry number from a KML/HTML description string."""
    match = re.search(r"(?:Gantry|gantry)\s*(?:No\.?|Number)?\s*[:#]?\s*([A-Za-z0-9-]+)", description or "")
    return match.group(1) if match else "Unknown"


def parse_erp_gantry_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse ERP gantry GeoJSON into simplified line segments."""
    gantries: List[Dict[str, Any]] = []
    for feature in data.get("features", []) if data else []:
        geometry = feature.get("geometry", {})
        properties = feature.get("properties", {})
        coordinates = geometry.get("coordinates", [])
        if geometry.get("type") == "LineString" and len(coordinates) >= 2:
            coords = [[lat, lon] for lon, lat, *_ in coordinates[:2]]
            description = properties.get("Description", "") or properties.get("description", "")
            gantry_num = extract_gantry_number(description)
            gantries.append(
                {
                    "coordinates": coords,
                    "gantry_num": gantry_num,
                    "unique_id": properties.get("Name") or properties.get("name") or f"kml_{gantry_num}",
                }
            )
    return gantries


def get_erp_gantry_data() -> List[Dict[str, Any]]:
    """Fetch and parse ERP gantry data with in-memory cache."""
    if _road_infra_cache.get("erp_gantries") is not None:
        return _road_infra_cache["erp_gantries"]
    raw_data = fetch_erp_gantry_data()
    parsed = parse_erp_gantry_data(raw_data or {})
    _road_infra_cache["erp_gantries"] = parsed
    return parsed
