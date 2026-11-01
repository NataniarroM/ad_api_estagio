import unittest
from fastapi.testclient import TestClient

from app.main import app

# Testes relacionados à integridade da API
class TestHealthCheck(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    # Teste de inicialização correta
    def test_home_returns_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

if __name__ == "__main__":
    unittest.main()