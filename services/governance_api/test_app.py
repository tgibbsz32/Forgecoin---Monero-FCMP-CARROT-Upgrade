"""Minimal security checks for the local-only governance prototype."""
import unittest
import os
import tempfile
import base58
from fastapi.testclient import TestClient
from nacl.signing import SigningKey
from services.governance_api.app import app, challenges, sessions
from services.governance_api import registry

class AuthTests(unittest.TestCase):
    def setUp(self):
        challenges.clear()
        sessions.clear()
        self.temp = tempfile.TemporaryDirectory()
        self.old_db = os.environ.get('FORGECOIN_GOVERNANCE_DB')
        os.environ['FORGECOIN_GOVERNANCE_DB'] = os.path.join(self.temp.name,'roles.sqlite3')
        self.client = TestClient(app)
        self.key = SigningKey.generate()
        self.address = base58.b58encode(self.key.verify_key.encode()).decode()

    def tearDown(self):
        if self.old_db is None: os.environ.pop('FORGECOIN_GOVERNANCE_DB',None)
        else: os.environ['FORGECOIN_GOVERNANCE_DB']=self.old_db
        self.temp.cleanup()

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

    def test_persistent_decisions_revoke_and_audit(self):
        login,_=self.login()
        headers={'Authorization':'Bearer '+login.json()['access_token']}
        registry.decide(self.address,'miner','approve','reviewer-a','verified sample mining contribution')
        self.assertEqual(registry.roles_for(self.address),{'miner'})
        self.assertTrue(self.client.get('/elections/miner/eligibility',headers=headers).json()['role_qualified'])
        self.assertFalse(self.client.get('/elections/miner/eligibility',headers=headers).json()['ballot_enabled'])
        registry.decide(self.address,'miner','revoke','reviewer-b','sample evidence invalidated')
        self.assertFalse(self.client.get('/elections/miner/eligibility',headers=headers).json()['role_qualified'])
        self.assertEqual(len(registry.history(self.address)),2)

    def test_no_public_role_grant_endpoint(self):
        login,_=self.login()
        headers={'Authorization':'Bearer '+login.json()['access_token']}
        self.assertEqual(self.client.post('/roles/grant',json={'role':'chamber'},headers=headers).status_code,404)

    def test_no_anonymous_access(self):
        self.assertEqual(self.client.get("/me").status_code, 401)
        self.assertEqual(self.client.get("/elections/chamber/eligibility").status_code, 401)

if __name__ == "__main__":
    unittest.main()
