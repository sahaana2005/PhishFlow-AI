
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
        self.assertEqual(result["risk_score"], 25)
        self.assertEqual(result["risk_level"], "Medium")
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
        self.assertEqual(result["risk_score"], 20)
        self.assertEqual(result["risk_level"], "Medium")
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

        self.assertFalse(result["suspicious"])
        self.assertEqual(result["risk_score"], 10)
        self.assertEqual(result["risk_level"], "Low")
        self.assertTrue(
            any(
                "longer than 100 characters" in warning
                for warning in result["warnings"]
            )
        )

    def test_url_shortener_triggers_warning(self):
        features = {
            "url_length": 25,
            "uses_url_shortener": True,
        }

        result = detect_suspicious_patterns(features)

        self.assertEqual(result["risk_score"], 10)
        self.assertEqual(result["risk_level"], "Low")
        self.assertFalse(result["suspicious"])
        self.assertTrue(
            any(
                "shortening service" in warning
                for warning in result["warnings"]
            )
        )

    def test_multiple_features_increase_risk_score(self):
        features = {
            "url_length": 150,
            "has_at_symbol": True,
            "host_is_ip": True,
            "subdomain_count": 3,
        }

        result = detect_suspicious_patterns(features)

        self.assertEqual(result["risk_score"], 70)
        self.assertEqual(result["risk_level"], "High")
        self.assertTrue(result["suspicious"])

    def test_no_matching_rules(self):
        features = {
            "url_length": 18,
            "uses_https": True,
            "has_at_symbol": False,
            "host_is_ip": False,
            "subdomain_count": 0,
            "has_hyphen_in_hostname": False,
            "uses_url_shortener": False,
            "matched_keywords": [],
        }

        result = detect_suspicious_patterns(features)

        self.assertFalse(result["suspicious"])
        self.assertEqual(result["risk_score"], 0)
        self.assertEqual(result["risk_level"], "Low")
        self.assertEqual(result["warnings"], [])
        self.assertEqual(result["warning_count"], 0)


if __name__ == "__main__":
    unittest.main()
