import json
import unittest
from services.pool_research.stratum_protocol import parse_request, SessionTable, ProtocolError

def msg(i,method,params):
    return json.dumps({"id":i,"method":method,"params":params}).encode()

class StratumProtocolTests(unittest.TestCase):
    def test_login_then_submit(self):
        t=SessionTable(limit=1); t.open("c1")
        with self.assertRaisesRegex(ProtocolError,"login required"):
            t.inspect("c1",msg(1,"keepalived",{}))
        t.inspect("c1",msg(1,"login",{"login":"FRG-test-address"}))
        submit={"id":"worker","job_id":"job1","nonce":"00000000","result":"00"*32}
        self.assertEqual(t.inspect("c1",msg(2,"submit",submit))["method"],"submit")
        with self.assertRaisesRegex(ProtocolError,"duplicate request"):
            t.inspect("c1",msg(2,"submit",submit))
    def test_limits_and_cleanup(self):
        t=SessionTable(limit=1);t.open("a")
        with self.assertRaisesRegex(ProtocolError,"capacity"):
            t.open("b")
        t.close("a")
        t.open("b")
    def test_invalid_frames(self):
        cases=[b"",b"[]",b"{}",b"{broken",b"\xff",b" "*4097,msg(1,"send_money",{}),msg(1,"login",{}),msg(1,"login",{"login":"x","unexpected":"field"}),msg(1,"submit",{"id":"a","job_id":"b","nonce":"not_hex!","result":"00"*32})]
        for case in cases:
            with self.subTest(case=case[:35]),self.assertRaises(ProtocolError):parse_request(case)
    def test_malformed_does_not_consume_id(self):
        t=SessionTable();t.open("a")
        with self.assertRaises(ProtocolError):t.inspect("a",msg(1,"login",{"login":""}))
        self.assertEqual(t.inspect("a",msg(1,"login",{"login":"address"}))["method"],"login")
    def test_cap_and_id_types(self):
        for limit in (0,101,1.0):
            with self.assertRaises(ValueError):SessionTable(limit)
        with self.assertRaises(ProtocolError):parse_request(msg(True,"keepalived",{}))

if __name__=="__main__":unittest.main()
