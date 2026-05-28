import unittest
from datetime import datetime, timedelta, timezone

from utils.realtime_weather_parsers import (
    normalize_unit,
    convert_to_kmh,
    is_within_singapore_bounds,
    is_within_last_5_minutes,
)


class TestRealtimeWeatherParsers(unittest.TestCase):
    def test_normalize_unit_known_replacements(self):
        self.assertEqual(normalize_unit("Degree Celsius", "X"), "°C")
        self.assertEqual(normalize_unit("Percentage", "X"), "%")

    def test_normalize_unit_default_fallback(self):
        self.assertEqual(normalize_unit(None, "mm"), "mm")
        self.assertEqual(normalize_unit("", "km/h"), "km/h")

    def test_convert_to_kmh(self):
        self.assertAlmostEqual(convert_to_kmh("10", "m/s"), 36.0)
        self.assertAlmostEqual(convert_to_kmh(12.5, "meters per second"), 45.0)
        self.assertEqual(convert_to_kmh(25, "km/h"), 25.0)
        self.assertIsNone(convert_to_kmh("bad", "m/s"))

    def test_singapore_bounds(self):
        self.assertTrue(is_within_singapore_bounds(1.30, 103.85))
        self.assertFalse(is_within_singapore_bounds(2.0, 103.85))
        self.assertFalse(is_within_singapore_bounds(1.30, 105.0))

    def test_is_within_last_5_minutes(self):
        now = datetime.now(timezone.utc)
        recent = (now - timedelta(minutes=2)).isoformat().replace("+00:00", "Z")
        old = (now - timedelta(minutes=8)).isoformat().replace("+00:00", "Z")
        self.assertTrue(is_within_last_5_minutes(recent))
        self.assertFalse(is_within_last_5_minutes(old))
        self.assertFalse(is_within_last_5_minutes(""))


if __name__ == "__main__":
    unittest.main()
