"""Minimal security checks for the local-only governance prototype."""
import unittest
import os
import tempfile
import base58
from fastapi.testclient import TestClient
from nacl.signing import SigningKey
from services.governance_api.app import app, challenges, sessions
from services.governance_api import registry, applications, elections

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

    def test_application_lifecycle_and_private_status(self):
        login,_=self.login()
        auth={'Authorization':'Bearer '+login.json()['access_token']}
        payload={'role':'miner','evidence_reference':'ref:private-mining-proof-0001',
                 'statement':'I have submitted mining evidence for eligibility review.'}
        self.assertEqual(self.client.post('/applications',json=payload).status_code,401)
        new=self.client.post('/applications',json=payload,headers=auth)
        self.assertEqual(new.status_code,201)
        app_id=new.json()['application_id']
        self.assertFalse(new.json()['votes_enabled'])
        self.assertEqual(self.client.post('/applications',json=payload,headers=auth).status_code,400)
        mine=self.client.get('/applications/mine',headers=auth).json()['applications']
        self.assertEqual(mine[0]['status'],'pending')
        self.assertNotIn('evidence_reference',mine[0])
        self.assertFalse(self.client.get('/elections/miner/eligibility',headers=auth).json()['role_qualified'])
        with self.assertRaises(ValueError):
            applications.review(app_id,'approve',self.address,'Self review prohibited')
        applications.review(app_id,'approve','independent-reviewer','Evidence independently examined')
        self.assertTrue(self.client.get('/elections/miner/eligibility',headers=auth).json()['role_qualified'])
        self.assertFalse(self.client.get('/elections/miner/eligibility',headers=auth).json()['ballot_enabled'])
        self.assertEqual(len(applications.audit(app_id)),2)
        with self.assertRaises(ValueError):
            applications.review(app_id,'reject','independent-reviewer','Cannot reject twice')

    def test_application_role_restrictions(self):
        login,_=self.login()
        auth={'Authorization':'Bearer '+login.json()['access_token']}
        payload={'role':'chamber','evidence_reference':'ref:fake-chamber-seat-001',
                 'statement':'I should not be able to self-enroll as a chamber representative.'}
        self.assertEqual(self.client.post('/applications',json=payload,headers=auth).status_code,400)
        payload['role']='staking'
        self.assertEqual(self.client.post('/applications',json=payload,headers=auth).status_code,400)
        self.assertEqual(self.client.post('/applications/1/approve',json={},headers=auth).status_code,404)

    def test_practice_snapshot_and_duplicate_ballots(self):
        login,_=self.login()
        headers={'Authorization':'Bearer '+login.json()['access_token']}
        with self.assertRaises(ValueError):
            elections.create('staking','Trial staking vote')
        eid=elections.create('miner','Trial miner election')
        self.assertEqual(self.client.post(f'/practice-elections/{eid}/ballots',
                         json={'choice':'yes'},headers=headers).status_code,403)
        registry.decide(self.address,'miner','approve','reviewer','Checked mined block')
        self.assertEqual(self.client.post(f'/practice-elections/{eid}/ballots',
                         json={'choice':'yes'},headers=headers).status_code,403)
        eid2=elections.create('miner','New miner election')
        self.assertEqual(self.client.post(f'/practice-elections/{eid2}/ballots',
                         json={'choice':'yes'},headers=headers).status_code,201)
        self.assertEqual(self.client.post(f'/practice-elections/{eid2}/ballots',
                         json={'choice':'no'},headers=headers).status_code,409)
        self.assertEqual(elections.detail(eid2)['ballots_cast'],1)
        self.assertFalse(elections.detail(eid2)['binding'])
        elections.close(eid2)
        self.assertEqual(self.client.post(f'/practice-elections/{eid2}/ballots',
                         json={'choice':'no'},headers=headers).status_code,409)

    def test_practice_rejects_anonymous_and_invalid_vote(self):
        eid=elections.create('community','Test public election')
        self.assertEqual(self.client.post(f'/practice-elections/{eid}/ballots',
                         json={'choice':'yes'}).status_code,401)
        login,_=self.login()
        headers={'Authorization':'Bearer '+login.json()['access_token']}
        self.assertEqual(self.client.post(f'/practice-elections/{eid}/ballots',
                         json={'choice':'arbitrary'},headers=headers).status_code,422)
        self.assertEqual(self.client.post('/practice-elections',json={'category':'miner'},
                         headers=headers).status_code,404)

    def test_operator_aggregates_closed_only(self):
        login,_=self.login()
        auth={'Authorization':'Bearer '+login.json()['access_token']}
        registry.decide(self.address,'community','approve','local-reviewer','Verified sample participation')
        eid=elections.create('community','Practice community decision')
        self.assertEqual(elections.detail(eid)['eligible_wallets'],1)
        self.assertEqual(len(elections.list_elections()),1)
        self.assertEqual(self.client.post(f'/practice-elections/{eid}/ballots',
                                        json={'choice':'yes'},headers=auth).status_code,201)
        with self.assertRaises(ValueError):
            elections.tally(eid)
        elections.close(eid)
        report=elections.tally(eid)
        self.assertEqual(report['results']['yes']['ballots'],1)
        self.assertEqual(report['results']['yes']['weight'],1)
        self.assertFalse(report['binding'])
        self.assertEqual(self.client.post('/admin/practice-elections',
                         json={'category':'community','title':'bad'},headers=auth).status_code,404)

    def test_no_anonymous_access(self):
        self.assertEqual(self.client.get("/me").status_code, 401)
        self.assertEqual(self.client.get("/elections/chamber/eligibility").status_code, 401)

if __name__ == "__main__":
    unittest.main()
