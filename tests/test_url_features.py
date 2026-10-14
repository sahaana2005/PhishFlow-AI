
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

    
    def test_empty_url_rejected(self):
        with self.assertRaises(ValueError):
            extract_url_features("")

    def test_whitespace_only_rejected(self):
        with self.assertRaises(ValueError):
            extract_url_features("   ")

    def test_plain_text_rejected(self):
        with self.assertRaises(ValueError):
            extract_url_features("hello world")

    def test_missing_hostname_rejected(self):
        with self.assertRaises(ValueError):
            extract_url_features("https:///login")

    def test_unsupported_scheme_rejected(self):
        with self.assertRaises(ValueError):
            extract_url_features("ftp://example.com")

    def test_non_text_input_rejected(self):
        with self.assertRaises(ValueError):
            extract_url_features(None)

    def test_invalid_port_rejected(self):
        with self.assertRaises(ValueError):
            extract_url_features("https://example.com:99999")



if __name__ == "__main__":
    unittest.main()
