import unittest
from unittest.mock import patch

from utils.async_fetcher import get_current_2min_bucket, get_current_10min_bucket


class TestAsyncFetcherBuckets(unittest.TestCase):
    @patch("utils.async_fetcher.time.time", return_value=1710000123.0)
    def test_2min_bucket_alignment(self, _mock_time):
        bucket = get_current_2min_bucket()
        self.assertEqual(bucket % 120, 0)
        self.assertLessEqual(bucket, 1710000123)

    @patch("utils.async_fetcher.time.time", return_value=1710000123.0)
    def test_10min_bucket_alignment(self, _mock_time):
        bucket = get_current_10min_bucket()
        self.assertEqual(bucket % 600, 0)
        self.assertLessEqual(bucket, 1710000123)

