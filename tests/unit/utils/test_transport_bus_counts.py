import unittest
from unittest.mock import patch

from utils.transport.bus import get_bus_services_count


class TestTransportBusCounts(unittest.TestCase):
    @patch(
        "utils.transport.bus.fetch_bus_routes_data",
        return_value={
            "value": [
                {"ServiceNo": "2"},
                {"ServiceNo": "2"},
                {"ServiceNo": "12"},
                {"ServiceNo": ""},
                {},
            ]
        },
    )
    def test_get_bus_services_count_unique_services_only(self, _mock_routes):
        self.assertEqual(get_bus_services_count(), 2)

    @patch("utils.transport.bus.fetch_bus_routes_data", return_value=None)
    def test_get_bus_services_count_no_data(self, _mock_routes):
        self.assertEqual(get_bus_services_count(), 0)
