
import unittest
import tempfile
from pathlib import Path

import app as app_module


class TestPhishFlowApp(unittest.TestCase):

    def setUp(self):
        # Create a temporary database for each test
        self.temp_dir = tempfile.TemporaryDirectory()

        app_module.DATABASE_PATH = (
            Path(self.temp_dir.name) / "test_phishflow.db"
        )

        app_module.initialize_database()

        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_homepage_loads(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"PhishFlow", response.data)

    def test_empty_url(self):
        response = self.client.post(
            "/",
            data={"url": ""}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Please enter a URL", response.data)

    def test_invalid_url(self):
        response = self.client.post(
            "/",
            data={"url": "ftp://invalid-example.com"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"HTTP", response.data)

    def test_valid_url_scan(self):
        response = self.client.post(
            "/",
            data={"url": "https://example.com"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Scan Result", response.data)

    def test_scan_history_updates(self):
        self.client.post(
            "/",
            data={"url": "https://example.com"}
        )

        history = app_module.get_scan_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["url"], "https://example.com")

    def test_dashboard_counts_scans(self):
        self.client.post(
            "/",
            data={"url": "https://example.com"}
        )

        stats = app_module.get_dashboard_stats()

        self.assertEqual(stats["total_scans"], 1)


if __name__ == "__main__":
    unittest.main()
