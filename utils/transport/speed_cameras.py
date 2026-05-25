"""Speed camera CSV helpers."""

from pathlib import Path

import pandas as pd

from utils.transport.cache import _road_infra_cache


def load_speed_camera_data() -> pd.DataFrame:
    """Load speed camera CSV data into a cached DataFrame."""
    if _road_infra_cache.get("speed_camera_df") is not None:
        return _road_infra_cache["speed_camera_df"]

    project_root = Path(__file__).resolve().parents[2]
    csv_path = project_root / "data" / "speed_camera.csv"
    if not csv_path.exists():
        return pd.DataFrame()

    df = pd.read_csv(csv_path)
    _road_infra_cache["speed_camera_df"] = df
    return df


def get_fixed_speed_camera_count() -> int:
    """Return count of fixed speed cameras."""
    df = load_speed_camera_data()
    if df.empty or "type_of_speed_camera" not in df.columns:
        return 0
    return int((df["type_of_speed_camera"] == "Fixed Speed Camera").sum())
