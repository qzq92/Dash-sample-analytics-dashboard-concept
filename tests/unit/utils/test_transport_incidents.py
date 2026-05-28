import unittest
from unittest.mock import patch

from utils.transport.incidents import _lta_headers


class TestTransportIncidentsHelpers(unittest.TestCase):
    @patch("utils.transport.incidents.os.getenv", return_value=None)
    def test_lta_headers_returns_none_without_api_key(self, _mock_getenv):
        self.assertIsNone(_lta_headers())

    @patch("utils.transport.incidents.os.getenv", return_value="abc123")
    def test_lta_headers_contains_expected_fields(self, _mock_getenv):
        headers = _lta_headers()
        self.assertIsNotNone(headers)
        self.assertEqual(headers["AccountKey"], "abc123")
        self.assertIn("User-Agent", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
