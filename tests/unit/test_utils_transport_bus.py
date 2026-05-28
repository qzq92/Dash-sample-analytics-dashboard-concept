import unittest

from utils.transport.bus import (
    calculate_bus_stop_viewport_bounds,
    filter_bus_stops_by_viewport,
)


class TestTransportBusViewportHelpers(unittest.TestCase):
    def test_calculate_bus_stop_viewport_bounds_returns_valid_range(self):
        min_lat, max_lat, min_lon, max_lon = calculate_bus_stop_viewport_bounds(
            center=[1.3521, 103.8198],
            zoom=13,
        )
        self.assertLess(min_lat, max_lat)
        self.assertLess(min_lon, max_lon)

    def test_filter_bus_stops_by_viewport(self):
        stops = [
            {"BusStopCode": "10001", "Latitude": "1.3521", "Longitude": "103.8198"},
            {"BusStopCode": "10002", "Latitude": "1.4500", "Longitude": "103.9500"},
            {"BusStopCode": "10003", "Latitude": "bad", "Longitude": "103.8198"},
        ]
        filtered = filter_bus_stops_by_viewport(stops, center=[1.3521, 103.8198], zoom=14)
        codes = {item["BusStopCode"] for item in filtered}
        self.assertIn("10001", codes)
        self.assertNotIn("10002", codes)
        self.assertNotIn("10003", codes)


if __name__ == "__main__":
    unittest.main()
