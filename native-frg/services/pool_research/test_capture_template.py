"""Exercise template capture only against a disposable local HTTP fixture."""
import json
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from unittest.mock import patch
from services.pool_research.capture_template import capture

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path=="/redirect":
            self.send_response(307)
            self.send_header("Location","http://example.com/json_rpc")
            self.end_headers()
            return
        if self.path!="/json_rpc":
            self.send_error(404);return
        count=int(self.headers.get("Content-Length","0"))
        body=json.loads(self.rfile.read(count))
        if body.get("method")!="get_block_template" or body["params"].get("reserve_size")!=8:
            self.send_error(400);return
        reply={"jsonrpc":"2.0","id":body["id"],"result":{
            "height":17,"difficulty":500000,"expected_reward":2384185222,
            "seed_hash":"a1"*32,"blocktemplate_blob":"01"*128,
            "blockhashing_blob":"02"*80,"reserved_offset":40}}
        data=json.dumps(reply).encode()
        self.send_response(200);self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(data)));self.end_headers()
        self.wfile.write(data)
    def log_message(self,*args):pass

class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown();cls.server.server_close();cls.thread.join(3)
    def test_local_fixture(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"sanitized.json"
            result=capture(f"http://127.0.0.1:{self.server.server_port}/json_rpc","DISPOSABLE_TEST_ADDRESS",path)
            self.assertEqual(result["height"],17)
            output=path.read_text()
            self.assertNotIn("DISPOSABLE_TEST_ADDRESS",output)
            self.assertNotIn("blocktemplate_blob",output)
    def test_reject_external_urls(self):
        with tempfile.TemporaryDirectory() as d:
            for url in ("https://127.0.0.1:39481/json_rpc","http://example.com/json_rpc",
                        "http://localhost:39481/json_rpc","http://127.0.0.1:39481/admin",
                        "http://user:pass@127.0.0.1:39481/json_rpc",
                        "http://127.0.0.1/json_rpc"):
                with self.subTest(url=url),self.assertRaises(ValueError):
                    capture(url,"TEST",Path(d)/"out.json")
    def test_redirect_never_followed(self):
        # Serve a redirect at an explicitly allowed /json_rpc endpoint.
        class RedirectHandler(Handler):
            def do_POST(self):
                self.send_response(307)
                self.send_header("Location","http://example.com/json_rpc")
                self.end_headers()
        server=ThreadingHTTPServer(("127.0.0.1",0),RedirectHandler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as d:
                output=Path(d)/"out.json"
                with self.assertRaises(HTTPError) as caught:
                    capture(f"http://127.0.0.1:{server.server_port}/json_rpc","TEST",output)
                self.assertEqual(caught.exception.code,307)
                self.assertFalse(output.exists())
        finally:
            server.shutdown();server.server_close();thread.join(3)
    def test_ignores_proxy_environment(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"sanitized.json"
            with patch.dict("os.environ",{"HTTP_PROXY":"http://127.0.0.1:1",
                                          "http_proxy":"http://127.0.0.1:1"},clear=False):
                result=capture(f"http://127.0.0.1:{self.server.server_port}/json_rpc","TEST",path)
            self.assertEqual(result["height"],17)

if __name__=="__main__":unittest.main()
