
import unittest

from src.url_features import extract_url_features


class TestURLFeatures(unittest.TestCase):

    def test_https_url(self):
        result = extract_url_features("https://google.com")
        self.assertTrue(result["uses_https"])

    def test_http_url(self):
        result = extract_url_features("http://example.com")
        self.assertFalse(result["uses_https"])

    def test_ip_address_host(self):
        result = extract_url_features("http://192.168.1.10/login")
        self.assertTrue(result["host_is_ip"])

    def test_domain_is_not_ip(self):
        result = extract_url_features("https://example.com")
        self.assertFalse(result["host_is_ip"])

    def test_at_symbol(self):
        result = extract_url_features("https://example.com@evil.test")
        self.assertTrue(result["has_at_symbol"])

    def test_url_length(self):
        url = "https://example.com"
        result = extract_url_features(url)
        self.assertEqual(result["url_length"], len(url))


if __name__ == "__main__":
    unittest.main()
