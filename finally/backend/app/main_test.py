import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app


class HealthEndpointTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_health_endpoint_returns_ok(self):
        response = self.client.get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_root_serves_dashboard_heading_amount_and_all_required_tickers(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("FinAlly", response.text)
        self.assertIn("$10,000", response.text)
        for ticker in ("AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM", "V", "NFLX"):
            with self.subTest(ticker=ticker):
                self.assertIn(ticker, response.text)

    def test_root_rejects_missing_frontend_export(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("app.main._frontend", Path(directory)):
                response = self.client.get("/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json(), {"detail": "Frontend export not found"})
        self.assertNotIn("Polecat", response.text)


if __name__ == "__main__":
    unittest.main()