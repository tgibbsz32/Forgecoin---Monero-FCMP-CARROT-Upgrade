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
    def test_ambiguous_json_objects_are_rejected(self):
        for frame in (
            b'{"id":1,"id":2,"method":"login","params":{"login":"test"}}',
            b'{"id":1,"method":"login","params":{"login":"test","login":"other"}}',
            b'{"id":1,"method":"login","params":{"login":"test","algo":["rx/0",NaN]}}',
        ):
            with self.subTest(frame=frame), self.assertRaises(ProtocolError):
                parse_request(frame)

    def test_xmrig_capabilities_and_jsonrpc_are_bounded(self):
        request = {"id": 1, "jsonrpc": "2.0", "method": "login",
                   "params": {"login": "synthetic", "algo": ["rx/0", "rx/wow"]}}
        self.assertEqual(parse_request(json.dumps(request).encode())["params"]["algo"][0], "rx/0")
        for value in ([], ["rx/0"]*65, [True], ["x"*33], ["bad\nname"], "rx/0"):
            request["params"]["algo"] = value
            with self.assertRaises(ProtocolError):parse_request(json.dumps(request).encode())
        request["params"]["algo"] = ["rx/0"]
        request["jsonrpc"] = "1.0"
        with self.assertRaises(ProtocolError):parse_request(json.dumps(request).encode())

if __name__=="__main__":unittest.main()
