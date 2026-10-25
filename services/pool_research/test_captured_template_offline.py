import unittest
from services.pool_research.tests.run_captured_template_offline import verify_capture
from services.pool_research.template_adapter import TemplateError
from services.pool_research.pow_boundary import VerificationError

class CaptureRunnerTests(unittest.TestCase):
    def fixture(self):
        header=b"\x11\x11\xac\x02"+b"\x33"*32+b"\x00"*4
        hashing=header+b"\x44"*32+b"\x01"
        block=header+b"\x55"*48
        return {"result":{"height":1,"difficulty":500000,"expected_reward":1,
             "seed_hash":"ab"*32,"blocktemplate_blob":block.hex(),
             "blockhashing_blob":hashing.hex(),"reserved_offset":len(block)-8}}
    def test_offline_uncredited_with_supplied_verifier(self):
        calls=[]
        def verifier(seed,blob):
            calls.append((seed,blob))
            return b"\xff"*32
        result=verify_capture(self.fixture(),verifier)
        self.assertEqual(result["status"],"LOW_DIFFICULTY")
        self.assertFalse(result["credited"])
        self.assertEqual(result["nonce_offset"],36)
        self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][0],b"\xab"*32)
        self.assertEqual(calls[0][1][36:40],b"\0"*4)
    def test_invalid_header_rejected_before_hashing(self):
        response=self.fixture()
        response["result"]["blocktemplate_blob"]="ff"+response["result"]["blocktemplate_blob"][2:]
        def no_call(seed,blob):
            self.fail("verifier must not be called")
        with self.assertRaises(VerificationError):
            verify_capture(response,no_call)
    def test_missing_raw_blobs_fails(self):
        response={"result":{"height":1,"difficulty":500000,
                            "expected_reward":1,"seed_hash":"ab"*32,
                            "blocktemplate_bytes":134,"hashing_bytes":76,
                            "reserved_offset":124}}
        with self.assertRaises(TemplateError):
            verify_capture(response,lambda a,b:b"\x00"*32)

if __name__=="__main__":unittest.main()
