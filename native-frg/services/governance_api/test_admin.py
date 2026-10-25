"""Security boundaries and complete local administrator workflow."""
import os
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from fastapi.testclient import TestClient
from services.governance_api.admin import create_app
from services.governance_api.app import app as public_app
from services.governance_api import applications, elections, registry


class AdminTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {
            "FORGECOIN_ENV": "development", "FORGECOIN_ADMIN_ENABLED": "1",
            "FORGECOIN_ADMIN_TOKEN": "a" * 43, "FORGECOIN_ADMIN_REVIEWER": "reviewer-test",
            "FORGECOIN_GOVERNANCE_DB": os.path.join(self.temp.name, "test.sqlite3"),
        })
        self.env.start()
        self.client = TestClient(create_app(), base_url="http://127.0.0.1:8766", client=("127.0.0.1", 12345))
        self.headers = {"Authorization": "Bearer " + "a" * 43}

    def tearDown(self):
        self.client.close()
        self.env.stop()
        self.temp.cleanup()

    def test_fail_closed_configuration(self):
        for change in ({"FORGECOIN_ENV": "production"}, {"FORGECOIN_ENV": ""}, {"FORGECOIN_ADMIN_ENABLED": "0"}, {"FORGECOIN_ADMIN_TOKEN": "short"}, {"FORGECOIN_ADMIN_REVIEWER": ""}):
            with patch.dict(os.environ, change), self.assertRaises(RuntimeError):
                create_app()

    def test_boundaries_and_assets(self):
        for path in ("/api/applications", "/api/elections", "/api/elections/1/tally"):
            self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.get(path, headers={"Authorization": "Bearer wallet-session"}).status_code, 401)
        for path in ("/api/elections", "/api/elections/1/close", "/api/applications/1/review"):
            self.assertEqual(self.client.post(path, json={}).status_code, 401)
        for hostile in ({"Origin": "https://evil.example"}, {"Origin": "null"}, {"Host": "evil.example"}, {"Sec-Fetch-Site": "cross-site"}):
            self.assertEqual(self.client.get("/api/applications", headers={**self.headers, **hostile}).status_code, 403)
        remote = TestClient(create_app(), base_url="http://127.0.0.1:8766", client=("192.0.2.1", 1234))
        self.assertEqual(remote.get("/api/applications", headers={**self.headers, "X-Forwarded-For": "127.0.0.1"}).status_code, 403)
        self.assertEqual(self.client.post("/api/elections", content="{}", headers=self.headers).status_code, 415)
        self.assertEqual(self.client.post("/api/elections", content="x" * 65537, headers={**self.headers, "Content-Type": "application/json"}).status_code, 413)
        for path in ("/", "/admin.js", "/admin.css"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["cache-control"], "no-store")
            self.assertIn("frame-ancestors 'none'", response.headers["content-security-policy"])
        public = TestClient(public_app)
        for path in ("/api/applications", "/admin.js", "/admin"):
            self.assertEqual(public.get(path, headers=self.headers).status_code, 404)
        self.assertFalse(public.get("/health").json()["binding_votes"])

    def test_review_election_workflow(self):
        aid = applications.submit("wallet-a", "community", "ref:test-evidence", "<script>alert('xss')</script>")
        pending = self.client.get("/api/applications", headers=self.headers).json()
        self.assertEqual(pending["applications"][0]["id"], aid)
        payload = {"action": "approve", "reason": "Independently checked evidence"}
        self.assertEqual(self.client.post(f"/api/applications/{aid}/review", json={**payload, "reviewer": "forged"}, headers=self.headers).status_code, 422)
        self.assertEqual(self.client.post(f"/api/applications/{aid}/review", json=payload, headers=self.headers).status_code, 200)
        self.assertEqual(applications.audit(aid)[-1]["actor"], "reviewer-test")
        self.assertEqual(self.client.post(f"/api/applications/{aid}/review", json=payload, headers=self.headers).status_code, 409)
        response = self.client.post("/api/elections", json={"category": "community", "title": "Practice proposal"}, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        eid = response.json()["id"]
        self.assertEqual(self.client.get(f"/api/elections/{eid}/tally", headers=self.headers).status_code, 409)
        registry.decide("late-wallet", "community", "approve", "reviewer", "Late approval")
        with self.assertRaises(PermissionError):
            elections.cast(eid, "late-wallet", "yes")
        elections.cast(eid, "wallet-a", "yes")
        overview = self.client.get("/api/elections", headers=self.headers).json()["elections"][0]
        self.assertEqual(overview["ballots_cast"], 1)
        self.assertNotIn("wallet-a", str(overview))
        self.assertEqual(self.client.post(f"/api/elections/{eid}/close", json={}, headers=self.headers).status_code, 200)
        with self.assertRaises(ValueError):
            elections.cast(eid, "wallet-a", "no")
        tally = self.client.get(f"/api/elections/{eid}/tally", headers=self.headers).json()
        self.assertFalse(tally["binding"])
        self.assertEqual(tally["results"]["yes"], {"ballots": 1, "weight": 1})
        self.assertEqual(self.client.post(f"/api/elections/{eid}/close", json={}, headers=self.headers).status_code, 409)

    def test_rejection_self_review_and_weights(self):
        aid = applications.submit("reviewer-test", "miner", "ref:test-proof", "Sample application evidence")
        self.assertEqual(self.client.post(f"/api/applications/{aid}/review", json={"action": "approve", "reason": "Self review denied"}, headers=self.headers).status_code, 409)
        aid = applications.submit("wallet-b", "miner", "ref:test-proof", "Sample application evidence")
        self.assertEqual(self.client.post(f"/api/applications/{aid}/review", json={"action": "reject", "reason": "Evidence inadequate"}, headers=self.headers).status_code, 200)
        self.assertEqual(registry.roles_for("wallet-b"), set())
        registry.decide("wallet-b", "staking", "approve", "reviewer", "Simulation only")
        for weights in (None, {"wallet-b": True}, {"wallet-b": -1}, {"wallet-b": 10**13}):
            self.assertEqual(self.client.post("/api/elections", json={"category": "staking", "title": "Demo stake", "weights": weights}, headers=self.headers).status_code, 422)
        eid = self.client.post("/api/elections", json={"category": "staking", "title": "Demo stake", "weights": {"wallet-b": 7}}, headers=self.headers).json()["id"]
        elections.cast(eid, "wallet-b", "abstain")
        elections.close(eid)
        self.assertEqual(elections.tally(eid)["results"]["abstain"]["weight"], 7)

    def test_simultaneous_reviews_only_one_decision(self):
        aid = applications.submit("wallet-a", "miner", "ref:test-proof", "Sample application evidence")
        def decide(action):
            try:
                applications.review(aid, action, "reviewer-test", "Evidence independently checked")
                return True
            except ValueError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            self.assertEqual(sum(pool.map(decide, ("approve", "reject"))), 1)
        self.assertEqual(len(applications.audit(aid)), 2)

    def test_close_serializes_with_ballot_transaction(self):
        from threading import Event
        registry.decide("wallet-a", "miner", "approve", "reviewer", "Verified evidence")
        eid = elections.create("miner", "Concurrent closing test")
        entered = Event()
        # Hold the closing transaction open while a ballot request starts.
        with elections.connect() as conn, ThreadPoolExecutor(max_workers=1) as pool:
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("UPDATE practice_elections SET status='closed' WHERE id=?", (eid,))

            def vote():
                entered.set()
                return elections.cast(eid, "wallet-a", "yes")

            future = pool.submit(vote)
            self.assertTrue(entered.wait(5))
            conn.commit()
            with self.assertRaises(ValueError):
                future.result(timeout=10)
        self.assertEqual(elections.detail(eid)["ballots_cast"], 0)


if __name__ == "__main__":
    unittest.main()
