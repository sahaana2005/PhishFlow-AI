
import unittest

from src.detection_engine import detect_suspicious_patterns


class TestDetectionEngine(unittest.TestCase):

    def test_ip_host_triggers_warning(self):
        features = {
            "url_length": 25,
            "uses_https": False,
            "has_at_symbol": False,
            "host_is_ip": True,
        }

        result = detect_suspicious_patterns(features)

        self.assertTrue(result["suspicious"])
        self.assertTrue(
            any("IP address" in warning for warning in result["warnings"])
        )

    def test_at_symbol_triggers_warning(self):
        features = {
            "url_length": 29,
            "uses_https": True,
            "has_at_symbol": True,
            "host_is_ip": False,
        }

        result = detect_suspicious_patterns(features)

        self.assertTrue(result["suspicious"])
        self.assertTrue(
            any("@ symbol" in warning for warning in result["warnings"])
        )

    def test_long_url_triggers_warning(self):
        features = {
            "url_length": 120,
            "uses_https": True,
            "has_at_symbol": False,
            "host_is_ip": False,
        }

        result = detect_suspicious_patterns(features)

        self.assertTrue(result["suspicious"])
        self.assertTrue(
            any("longer than 100 characters" in warning
                for warning in result["warnings"])
        )

    def test_no_matching_rules(self):
        features = {
            "url_length": 18,
            "uses_https": True,
            "has_at_symbol": False,
            "host_is_ip": False,
        }

        result = detect_suspicious_patterns(features)

        self.assertFalse(result["suspicious"])
        self.assertEqual(result["warnings"], [])


if __name__ == "__main__":
    unittest.main()
