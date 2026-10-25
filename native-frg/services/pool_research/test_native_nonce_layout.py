import unittest
from dataclasses import replace
from services.pool_research.native_nonce_layout import (
    nonce_offset, verify_header_nonce, replace_nonce_in_hashing_blob)
from services.pool_research.template_adapter import validate_template, TemplateError

def fixture(timestamp=b"\xac\x02", nonce=b"\x01\x02\x03\x04"):
    header=b"\x11\x11"+timestamp+b"\x33"*32+nonce
    # Hashing blob contains serialized header + 32-byte Merkle root + tx count.
    hashing=header+b"\x44"*32+b"\x01"
    block=header+b"\x55"*48
    return validate_template({"result":{
        "height":1,"difficulty":500000,"expected_reward":2384185222,
        "seed_hash":"ab"*32,"blockhashing_blob":hashing.hex(),
        "blocktemplate_blob":block.hex(),"reserved_offset":len(block)-8}})

class NonceLayoutTests(unittest.TestCase):
    def test_variable_length_timestamp(self):
        for timestamp, offset in ((b"\x01",35),(b"\xac\x02",36),(b"\x80\x80\x01",37)):
            with self.subTest(timestamp=timestamp):
                self.assertEqual(verify_header_nonce(fixture(timestamp)),offset)

    def test_nonce_replacement_changes_only_four_bytes(self):
        t=fixture()
        offset=verify_header_nonce(t)
        b=replace_nonce_in_hashing_blob(t,0xA1B2C3D4)
        self.assertEqual(b[offset:offset+4],b"\xd4\xc3\xb2\xa1")
        self.assertEqual(b[:offset],t.blockhashing_blob[:offset])
        self.assertEqual(b[offset+4:],t.blockhashing_blob[offset+4:])
        self.assertEqual(t.blockhashing_blob[offset:offset+4],b"\x01\x02\x03\x04")

    def test_reject_mismatched_block_header(self):
        t=fixture()
        with self.assertRaises(TemplateError):
            verify_header_nonce(replace(t,blocktemplate_blob=b"\x12"+t.blocktemplate_blob[1:]))

    def test_invalid_nonce_values(self):
        t=fixture()
        for n in (-1,0x100000000,True,1.5,"1"):
            with self.subTest(n=n),self.assertRaises(ValueError):
                replace_nonce_in_hashing_blob(t,n)

    def test_invalid_varints_and_truncation(self):
        for data in (b"",b"\x80",b"\x80\x00",b"\xff"*10,b"\x01\x01\x01"+b"\x00"*34):
            with self.subTest(data=data),self.assertRaises(TemplateError):
                nonce_offset(data)

if __name__=="__main__":unittest.main()
