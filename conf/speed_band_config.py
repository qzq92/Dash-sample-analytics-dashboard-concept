"""
Speed band mapping configuration.
Maps speed band numbers to speed ranges in km/h.
Reference: LTA DataMall Traffic Speed Bands API
"""
from typing import Tuple, Union

# Speed band to speed range mapping (in km/h)
# Format: band_number: (min_speed, max_speed)
SPEED_BAND_RANGES = {
    1: (0, 9),      # 0 < 9 km/h
    2: (10, 19),    # 10 < 19 km/h
    3: (20, 29),    # 20 < 29 km/h
    4: (30, 39),    # 30 < 39 km/h
    5: (40, 49),    # 40 < 49 km/h
    6: (50, 59),    # 50 < 59 km/h
    7: (60, 69),    # 60 < 69 km/h
    8: (70, 100),   # 70+ km/h (using 100 as upper bound for calculation)
}


def get_speed_range(band: Union[int, str]) -> Tuple[int, int]:
    """
    Get the speed range for a given speed band.

    Args:
        band: Speed band number (1-8)

    Returns:
        Tuple of (min_speed, max_speed) in km/h, or (0, 0) if invalid
    """
    return SPEED_BAND_RANGES.get(band, (0, 0))


def get_speed_midpoint(band: Union[int, str]) -> float:
    """
    Get the midpoint speed for a given speed band.

    Args:
        band: Speed band number (1-8)

    Returns:
        Midpoint speed in km/h, or 0 if invalid
    """
    min_speed, max_speed = get_speed_range(band)
    if min_speed == 0 and max_speed == 0:
        return 0
    return (min_speed + max_speed) / 2

