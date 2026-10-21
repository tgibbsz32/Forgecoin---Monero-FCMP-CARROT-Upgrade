"""Minimal security checks for the local-only governance prototype."""
import unittest
import base58
from fastapi.testclient import TestClient
from nacl.signing import SigningKey
from services.governance_api.app import app, challenges, sessions, verified_roles

class AuthTests(unittest.TestCase):
    def setUp(self):
        challenges.clear()
        sessions.clear()
        verified_roles.clear()
        self.client = TestClient(app)
        self.key = SigningKey.generate()
        self.address = base58.b58encode(self.key.verify_key.encode()).decode()

    def login(self):
        res = self.client.post("/auth/challenge", json={"address": self.address})
        self.assertEqual(res.status_code, 200)
        obj = res.json()
        sig = base58.b58encode(self.key.sign(obj["message"].encode()).signature).decode()
        payload = {"address": self.address, "nonce": obj["nonce"], "signature": sig}
        return self.client.post("/auth/verify", json=payload), payload

    def test_login_role_denied_and_replay_blocked(self):
        login, payload = self.login()
        self.assertEqual(login.status_code, 200)
        token = login.json()["access_token"]
        headers = {"Authorization": "Bearer " + token}
        self.assertEqual(self.client.get("/me", headers=headers).json()["verified_roles"], [])
        res = self.client.get("/elections/miner/eligibility", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()["ballot_enabled"])
        self.assertFalse(res.json()["role_qualified"])
        self.assertEqual(self.client.post("/auth/verify", json=payload).status_code, 401)

    def test_invalid_signature_does_not_authenticate(self):
        chal = self.client.post("/auth/challenge", json={"address": self.address}).json()
        wrong_key = SigningKey.generate()
        sig = base58.b58encode(wrong_key.sign(chal["message"].encode()).signature).decode()
        res = self.client.post("/auth/verify", json={"address": self.address, "nonce": chal["nonce"], "signature": sig})
        self.assertEqual(res.status_code, 401)

    def test_no_anonymous_access(self):
        self.assertEqual(self.client.get("/me").status_code, 401)
        self.assertEqual(self.client.get("/elections/chamber/eligibility").status_code, 401)

if __name__ == "__main__":
    unittest.main()
