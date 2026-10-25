import unittest
from services.pool_research.share_preflight import SharePreflight,SharePreflightError
from services.pool_research.pow_boundary import verify_offline_share,VerificationError

class PowBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.gate=SharePreflight()
        self.gate.register("job1",1)
        self.blob=bytes(76)
    def run_share(self,nonce="01020304",difficulty=500000,verifier=None):
        return verify_offline_share(self.gate,"job1",nonce,1,self.blob,39,difficulty,verifier)
    def test_no_verifier_rejected_without_reservation(self):
        with self.assertRaises(VerificationError):self.run_share()
        self.assertEqual(len(self.gate.seen),0)
    def test_success_is_never_credited(self):
        value=self.run_share(verifier=lambda blob:bytes(32))
        self.assertEqual(value.status,"POW_THRESHOLD_MET_UNCREDITED")
        self.assertNotEqual(value.status,"ACCEPTED")
    def test_low_difficulty(self):
        value=self.run_share(verifier=lambda blob:b"\xff"*32)
        self.assertEqual(value.status,"LOW_DIFFICULTY")
    def test_nonce_little_endian_is_not_swapped(self):
        def check(blob):
            self.assertEqual(blob[39:43],bytes.fromhex("aabbccdd"))
            self.assertEqual(blob[:39]+blob[43:],self.blob[:39]+self.blob[43:])
            return bytes(32)
        self.run_share(nonce="aabbccdd",verifier=check)
    def test_bad_digest(self):
        with self.assertRaises(VerificationError):
            self.run_share(verifier=lambda blob:b"\x00")
    def test_failed_verifier(self):
        def broken(blob):raise RuntimeError("internal")
        with self.assertRaises(VerificationError):
            self.run_share(verifier=broken)
    def test_invalid_difficulty_not_reserved(self):
        for diff in (0,True,-1,1<<128):
            with self.subTest(diff=diff),self.assertRaises(VerificationError):
                self.run_share(difficulty=diff,verifier=lambda _:bytes(32))
        self.assertEqual(len(self.gate.seen),0)
    def test_duplicate_rejected(self):
        self.run_share(verifier=lambda _:bytes(32))
        with self.assertRaises(SharePreflightError):
            self.run_share(verifier=lambda _:bytes(32))
    def test_invalid_offset_not_reserved(self):
        with self.assertRaises(VerificationError):
            verify_offline_share(self.gate,"job1","01020304",1,self.blob,76,500000,lambda _:bytes(32))
        self.assertEqual(len(self.gate.seen),0)

if __name__=="__main__":unittest.main()
