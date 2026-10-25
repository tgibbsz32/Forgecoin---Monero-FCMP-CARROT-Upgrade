"""Real subprocess fault tests with a fake worker; no native PoW claims."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from .native_randomx_adapter import NativeRandomXError
from .persistent_randomx import PersistentRandomXAdapter

WORKER = '''import hashlib,os,pathlib,sys,time
mode=sys.argv[1]
marker=pathlib.Path(sys.argv[2])
if mode in ("crash-once","hang-once") and not marker.exists():
    marker.write_text("used")
    if mode=="crash-once":os._exit(2)
    time.sleep(20)
for line in sys.stdin.buffer:
    tag,seed,blob=line.decode().strip().split(" ")
    if mode=="wrong-tag":tag="999"
    if mode=="long":
        print("x"*200,flush=True)
        continue
    digest=hashlib.sha256(bytes.fromhex(seed)+bytes.fromhex(blob)).hexdigest()
    print(tag+" "+digest,flush=True)
'''


class PersistentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.script = Path(self.temp.name) / "fake_worker.py"
        self.script.write_text(WORKER)

    def adapter(self, mode="normal", timeout=2):
        adapter = PersistentRandomXAdapter(sys.executable, timeout=timeout,
            arguments=["-u", str(self.script), mode, str(Path(self.temp.name)/"marker")])
        self.addCleanup(adapter.close)
        return adapter

    def test_reuses_process_and_recycles_after_request_limit(self):
        adapter = self.adapter()
        for i in range(65):
            seed, blob = bytes([i % 2])*32, bytes([i])
            self.assertEqual(adapter(seed, blob), hashlib.sha256(seed+blob).digest())
        self.assertEqual(adapter.starts, 2)
        self.assertEqual(adapter.requests, 1)

    def test_crash_refused_then_next_explicit_request_recovers(self):
        adapter = self.adapter("crash-once")
        with self.assertRaises(NativeRandomXError):
            adapter(bytes(32), b"test")
        self.assertIsNone(adapter.process)
        self.assertEqual(adapter(bytes(32), b"test"), hashlib.sha256(bytes(32)+b"test").digest())
        self.assertEqual(adapter.starts, 2)

    def test_timeout_covers_blocked_stdin_and_reaps_worker(self):
        adapter = self.adapter("hang-once", timeout=0.2)
        with self.assertRaises(NativeRandomXError):
            adapter(bytes(32), b"a"*262144)
        self.assertIsNone(adapter.process)
        self.assertFalse(adapter.broken)
        adapter.timeout = 2
        self.assertEqual(adapter(bytes(32), b"test"), hashlib.sha256(bytes(32)+b"test").digest())

    def test_stale_tag_and_overlong_output_are_refused(self):
        for mode in ("wrong-tag", "long"):
            with self.subTest(mode=mode):
                adapter = self.adapter(mode)
                with self.assertRaises(NativeRandomXError):
                    adapter(bytes(32), b"test")
                self.assertIsNone(adapter.process)

    def test_bad_inputs_do_not_spawn_and_closed_adapter_stays_closed(self):
        adapter = self.adapter()
        with patch("services.pool_research.persistent_randomx.subprocess.Popen") as spawn:
            for seed, blob in ((bytes(31), b"a"), (bytes(32), b""),
                               (bytes(32), b"a"*262145)):
                with self.assertRaises(NativeRandomXError):
                    adapter(seed, blob)
            spawn.assert_not_called()
        adapter.close()
        with self.assertRaises(NativeRandomXError):
            adapter(bytes(32), b"test")

    def test_concurrent_call_fails_without_spawning(self):
        adapter = self.adapter()
        with adapter.lock:
            with self.assertRaises(NativeRandomXError):
                adapter(bytes(32), b"test")
        self.assertEqual(adapter.starts, 0)


if __name__ == "__main__":
    unittest.main()
