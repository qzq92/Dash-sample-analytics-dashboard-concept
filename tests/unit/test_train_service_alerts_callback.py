import unittest

from callbacks.train_service_alerts_callback import format_mrt_line_operational_details


class TestTrainServiceAlertsCallback(unittest.TestCase):
    def test_format_mrt_line_operational_details_uses_status_text_override(self):
        mrt_display, _lrt_display = format_mrt_line_operational_details(
            data={},
            line_status_map_override={
                "NSL": {"status": 2, "has_message": True, "status_text": "Delayed*"}
            },
        )

        first_line_card = mrt_display.children[0]
        status_label = first_line_card.children[1]
        self.assertEqual(status_label.children, "Delayed*")
