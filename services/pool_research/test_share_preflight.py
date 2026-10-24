import unittest
from services.pool_research.share_preflight import SharePreflight,SharePreflightError

class SharePreflightTests(unittest.TestCase):
    def setUp(self):
        self.gate=SharePreflight()
        self.gate.register("job1",1)
    def test_ready_is_not_accepted(self):
        self.assertEqual(self.gate.inspect("job1","00000000",1),"READY_FOR_POW")
    def test_duplicate_across_workers_case_insensitive(self):
        self.gate.inspect("job1","a0b0c0d0",1)
        with self.assertRaises(SharePreflightError):
            self.gate.inspect("job1","A0B0C0D0",1)
    def test_stale_and_unknown(self):
        for job,height in (("job1",2),("unknown",1)):
            with self.assertRaises(SharePreflightError):self.gate.inspect(job,"00000000",height)
    def test_bad_nonce(self):
        for nonce in ("", "abcdefg", "abcdefghi", "zzzzzzzz", 0, None):
            with self.subTest(nonce=nonce),self.assertRaises(SharePreflightError):
                self.gate.inspect("job1",nonce,1)
    def test_invalid_height(self):
        for height in (0,True,-1,"1"):
            with self.assertRaises(SharePreflightError):self.gate.inspect("job1","00000000",height)
    def test_duplicate_registration(self):
        with self.assertRaises(SharePreflightError):self.gate.register("job1",1)
    def test_stale_does_not_consume_nonce(self):
        with self.assertRaises(SharePreflightError):self.gate.inspect("job1","abababab",2)
        self.assertEqual(self.gate.inspect("job1","abababab",1),"READY_FOR_POW")
    def test_register_invalid_job(self):
        for job in ("", "bad job", "é", "x"*65, None):
            with self.assertRaises(SharePreflightError):self.gate.register(job,1)
    def test_separate_jobs_same_nonce(self):
        self.gate.register("job2",1)
        self.assertEqual(self.gate.inspect("job1","00000000",1),"READY_FOR_POW")
        self.assertEqual(self.gate.inspect("job2","00000000",1),"READY_FOR_POW")

if __name__=="__main__":unittest.main()
