import sys
import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestSENAContigo(unittest.TestCase):

    def test_1_login_superadmin(self):
        resp = client.post("/api/auth/login", json={
            "correo": "admin@sena.edu.co",
            "password": "Sena12345!"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["usuario"]["rol"], "superadmin")

    def test_2_login_aprendiz(self):
        resp = client.post("/api/auth/login", json={
            "correo": "aprendiz.juan@misena.edu.co",
            "password": "Sena12345!"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["usuario"]["rol"], "aprendiz")

    def test_3_get_regionales(self):
        login_resp = client.post("/api/auth/login", json={
            "correo": "admin@sena.edu.co",
            "password": "Sena12345!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/organizacion/regionales", headers=headers)
        self.assertEqual(resp.status_code, 200)
        regionales = resp.json()
        self.assertGreaterEqual(len(regionales), 3)

    def test_4_get_variables(self):
        login_resp = client.post("/api/auth/login", json={
            "correo": "admin@sena.edu.co",
            "password": "Sena12345!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/variables/", headers=headers)
        self.assertEqual(resp.status_code, 200)
        variables = resp.json()
        self.assertGreater(len(variables), 0)

    def test_5_analytics(self):
        login_resp = client.post("/api/auth/login", json={
            "correo": "admin@sena.edu.co",
            "password": "Sena12345!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp_act = client.get("/api/analytics/estado-actual", headers=headers)
        self.assertEqual(resp_act.status_code, 200)

        resp_evo = client.get("/api/analytics/evolucion-longitudinal", headers=headers)
        self.assertEqual(resp_evo.status_code, 200)

    def test_6_casos(self):
        login_resp = client.post("/api/auth/login", json={
            "correo": "admin@sena.edu.co",
            "password": "Sena12345!"
        })
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/casos/", headers=headers)
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.json(), list)


if __name__ == "__main__":
    unittest.main()
