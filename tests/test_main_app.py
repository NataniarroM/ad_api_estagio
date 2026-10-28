import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestHealthCheck(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_homeu_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

if __name__ == "__main__":
    unittest.main()