"""Only identity/staleness tests; no mining, sockets or payout logic."""
import unittest
from dataclasses import replace
from services.pool_research.template_adapter import validate_template, TemplateError
from services.pool_research.job_envelope import build_job_envelope, is_stale

def fixture():
    return validate_template({"result":{
        "height":1, "difficulty":500000, "expected_reward":2384185222,
        "seed_hash":"2a91ebe3007fb301072c5b0c8e130c782d1218e4633f6a30e6c2d692b6ac5f05",
        "blocktemplate_blob":"01"*134, "blockhashing_blob":"02"*76,
        "reserved_offset":124}}, reserve_size=8)

class JobEnvelopeTests(unittest.TestCase):
    def test_deterministic_identity_and_session_isolation(self):
        t=fixture()
        a=build_job_envelope(t,"worker_1")
        self.assertEqual(a,build_job_envelope(t,"worker_1"))
        self.assertNotEqual(a.job_id,build_job_envelope(t,"worker_2").job_id)
        self.assertEqual(len(a.job_id),32)
        self.assertEqual(a.height,1)
        self.assertEqual(a.difficulty,500000)
        self.assertFalse(hasattr(a,"blob"))
        self.assertFalse(hasattr(a,"target"))

    def test_changed_template_changes_identity(self):
        a=fixture()
        b=replace(a,blocktemplate_blob=b"\x03"+a.blocktemplate_blob[1:])
        self.assertNotEqual(build_job_envelope(a,"worker").job_id,
                            build_job_envelope(b,"worker").job_id)

    def test_stale_on_height_change(self):
        j=build_job_envelope(fixture(),"worker")
        self.assertFalse(is_stale(j,1))
        self.assertTrue(is_stale(j,2))
        with self.assertRaises(ValueError):is_stale(j,True)

    def test_reject_invalid_session_and_bounds(self):
        t=fixture()
        for s in ("", "two words", "x"*65, "é", "../wallet"):
            with self.subTest(s=s),self.assertRaises(ValueError):
                build_job_envelope(t,s)
        with self.assertRaises(TemplateError):
            build_job_envelope(replace(t,reserved_offset=128),"worker")

if __name__=="__main__":unittest.main()
