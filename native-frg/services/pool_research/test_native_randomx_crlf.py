import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from services.pool_research.native_randomx_adapter import NativeRandomXAdapter, NativeRandomXError

class NativeLineEndingTests(unittest.TestCase):
    def test_crlf_and_lf(self):
        with TemporaryDirectory() as directory:
            path=Path(directory)/"rx.exe"
            path.write_bytes(b"placeholder")
            adapter=NativeRandomXAdapter(path)
            for ending in (b"",b"\n",b"\r\n"):
                with self.subTest(ending=ending), patch(
                    "services.pool_research.native_randomx_adapter.subprocess.run",
                    return_value=subprocess.CompletedProcess([],0,b"a"*64+ending,b"")
                ):
                    self.assertEqual(adapter(bytes(32),b"\x01"),bytes.fromhex("aa"*32))
            for bad in (b"a"*64+b"\r",b"a"*64+b"\r\n\n",b"a"*64+b" \n"):
                with self.subTest(bad=bad[-4:]),patch(
                    "services.pool_research.native_randomx_adapter.subprocess.run",
                    return_value=subprocess.CompletedProcess([],0,bad,b"")
                ):
                    with self.assertRaises(NativeRandomXError):
                        adapter(bytes(32),b"\x01")
if __name__=="__main__":unittest.main()
