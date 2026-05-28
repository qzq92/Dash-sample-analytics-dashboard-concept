import unittest
from unittest.mock import patch

from utils.realtime_weather_api import fetch_realtime_data, fetch_realtime_data_async


class TestRealtimeWeatherApiHelpers(unittest.TestCase):
    def test_fetch_realtime_data_returns_none_for_unsupported_endpoint(self):
        self.assertIsNone(fetch_realtime_data("unsupported-endpoint"))

    def test_fetch_realtime_data_async_returns_none_for_unsupported_endpoint(self):
        self.assertIsNone(fetch_realtime_data_async("unsupported-endpoint"))

    @patch("utils.realtime_weather_api.fetch_url_2min_cached", return_value={"ok": True})
    def test_fetch_realtime_data_calls_shared_cached_fetch(self, mock_fetch):
        data = fetch_realtime_data("air-temperature")
        self.assertEqual(data, {"ok": True})
        mock_fetch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
