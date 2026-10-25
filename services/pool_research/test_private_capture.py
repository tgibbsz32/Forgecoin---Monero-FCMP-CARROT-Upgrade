import json
import tempfile
import unittest
from pathlib import Path
from services.pool_research.private_capture import persist_private_capture
from services.pool_research.template_adapter import validate_template

def fixture():
    h=b"\x11\x11\xac\x02"+b"\x33"*32+b"\x00"*4
    block=h+b"\x55"*48
    hashing=h+b"\x44"*32+b"\x01"
    return {"jsonrpc":"2.0","id":"private","result":{
        "height":1,"difficulty":500000,"expected_reward":1,
        "seed_hash":"ab"*32,"blocktemplate_blob":block.hex(),
        "blockhashing_blob":hashing.hex(),
        "reserved_offset":len(block)-8,
        "wallet_address":"DO_NOT_PERSIST","private_note":"DO_NOT_PERSIST"}}

class PrivateCaptureTests(unittest.TestCase):
    def test_roundtrip_without_extraneous_fields(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"template.json"
            metadata=persist_private_capture(fixture(),p)
            body=p.read_text()
            self.assertNotIn("DO_NOT_PERSIST",body)
            result=json.loads(body)
            self.assertEqual(set(result),{"result"})
            t=validate_template(result)
            self.assertEqual(t.height,1)
            self.assertEqual(metadata["hashing_blob_size"],73)
    def test_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"template.json"
            p.write_text("existing")
            with self.assertRaises(FileExistsError):persist_private_capture(fixture(),p)
            self.assertEqual(p.read_text(),"existing")
    def test_reject_invalid_before_write(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"template.json"
            invalid=fixture()
            del invalid["result"]["blockhashing_blob"]
            with self.assertRaises(ValueError):persist_private_capture(invalid,p)
            self.assertFalse(p.exists())

if __name__=="__main__":unittest.main()
