import unittest
from dataclasses import replace
from services.pool_research.template_adapter import validate_template
from services.pool_research.bound_job import BoundJobVerifier
from services.pool_research.pow_boundary import VerificationError
from services.pool_research.share_preflight import SharePreflightError

def fixture():
    header=b"\x11\x11\xac\x02"+b"\x33"*32+b"\x00"*4
    hashing=header+b"\x44"*32+b"\x01"
    block=header+b"\x55"*48
    return validate_template({"result":{"height":1,"difficulty":500000,"expected_reward":2384185222,
        "seed_hash":"ab"*32,"blocktemplate_blob":block.hex(),
        "blockhashing_blob":hashing.hex(),"reserved_offset":len(block)-8}})

class BoundJobTests(unittest.TestCase):
    def setUp(self):
        self.store=BoundJobVerifier()
        self.job=self.store.register(fixture(),500000)
    def test_registered_data_is_canonical_for_callback(self):
        def verifier(seed,blob):
            self.assertEqual(seed,b"\xab"*32)
            self.assertEqual(blob[36:40],bytes.fromhex("01020304"))
            self.assertEqual(len(blob),73)
            return bytes(32)
        result=self.store.inspect(self.job,"01020304",1,verifier)
        self.assertEqual(result.status,"POW_THRESHOLD_MET_UNCREDITED")
    def test_no_verifier_does_not_consume(self):
        with self.assertRaises(VerificationError):
            self.store.inspect(self.job,"00000001",1,None)
        self.assertEqual(self.store.inspect(self.job,"00000001",1,lambda s,b:bytes(32)).status,"POW_THRESHOLD_MET_UNCREDITED")
    def test_duplicate(self):
        self.store.inspect(self.job,"ff000000",1,lambda s,b:bytes(32))
        with self.assertRaises(SharePreflightError):
            self.store.inspect(self.job,"FF000000",1,lambda s,b:bytes(32))
    def test_stale_unknown(self):
        with self.assertRaises(SharePreflightError):
            self.store.inspect(self.job,"00000002",2,lambda s,b:bytes(32))
        with self.assertRaises(VerificationError):
            self.store.inspect("unknown","00000002",1,lambda s,b:bytes(32))
    def test_bad_header(self):
        t=fixture()
        with self.assertRaises(VerificationError):
            BoundJobVerifier().register(replace(t,blocktemplate_blob=b"\xff"+t.blocktemplate_blob[1:]),500000)
    def test_different_worker_difficulty_changes_id(self):
        other=BoundJobVerifier().register(fixture(),400000)
        self.assertNotEqual(other,self.job)
    def test_low_difficulty_never_credited(self):
        result=self.store.inspect(self.job,"aa000000",1,lambda s,b:b"\xff"*32)
        self.assertEqual(result.status,"LOW_DIFFICULTY")

if __name__=="__main__":unittest.main()
