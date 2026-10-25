import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from services.pool_research.native_randomx_adapter import NativeRandomXAdapter, NativeRandomXError

class NativeRandomXAdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.exe=Path(self.tmp.name)/"rx.exe"
        self.exe.write_bytes(b"placeholder")
        self.adapter=NativeRandomXAdapter(self.exe)

    def test_valid_digest_and_arguments(self):
        expected=b"\x7c"*32
        with patch("services.pool_research.native_randomx_adapter.subprocess.run",
                   return_value=subprocess.CompletedProcess([],0,expected.hex().encode()+b"\n",b"")) as run:
            self.assertEqual(self.adapter(b"\xaa"*32,b"\x01"*76),expected)
        args=run.call_args.args[0]
        self.assertEqual(args[1], "aa"*32)
        self.assertEqual(args[2], "01"*76)
        self.assertEqual(run.call_args.kwargs["stdin"],subprocess.DEVNULL)

    def test_missing_verifier_input_rejected_pre_spawn(self):
        with patch("services.pool_research.native_randomx_adapter.subprocess.run") as run:
            for seed,blob in ((b"\x00"*31,b"\x01"),(b"\x00"*32,b""),(b"\x00"*32,b"\x01"*262145)):
                with self.assertRaises(NativeRandomXError):
                    self.adapter(seed,blob)
            run.assert_not_called()

    def test_native_exit_failure(self):
        with patch("services.pool_research.native_randomx_adapter.subprocess.run",
                   return_value=subprocess.CompletedProcess([],1,b"",b"error")):
            with self.assertRaises(NativeRandomXError):self.adapter(b"\x00"*32,b"\x01")

    def test_malformed_native_output(self):
        for output in (b"",b"zz"*32,b"A"*64,b"f"*64+b"extra",b"f"*63,b"f"*64+b"\n\n"):
            with self.subTest(output=output[:8]),patch("services.pool_research.native_randomx_adapter.subprocess.run",
                       return_value=subprocess.CompletedProcess([],0,output,b"")):
                with self.assertRaises(NativeRandomXError):self.adapter(b"\x00"*32,b"\x01")

    def test_timeout(self):
        with patch("services.pool_research.native_randomx_adapter.subprocess.run",
                   side_effect=subprocess.TimeoutExpired("rx",1)):
            with self.assertRaises(NativeRandomXError):self.adapter(b"\x00"*32,b"\x01")

    def test_bad_timeout(self):
        for value in (0,61,True,-1):
            with self.assertRaises(NativeRandomXError):NativeRandomXAdapter(self.exe,value)

if __name__=="__main__":unittest.main()
