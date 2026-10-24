import tempfile
import unittest
from pathlib import Path
from services.pool_research.isolated_daemon import offline_daemon_args

class IsolatedDaemonTests(unittest.TestCase):
    def test_offline_loopback_only(self):
        with tempfile.TemporaryDirectory() as d:
            exe=Path(d)/"forged.exe";exe.write_bytes(b"test fixture")
            argv=offline_daemon_args(exe,Path(d)/"fresh")
            self.assertIn("--offline",argv)
            self.assertIn("--no-igd",argv)
            for flag in ("--rpc-bind-ip","--p2p-bind-ip","--zmq-rpc-bind-ip"):
                self.assertEqual(argv[argv.index(flag)+1],"127.0.0.1")
    def test_reject_existing_data_and_duplicate_ports(self):
        with tempfile.TemporaryDirectory() as d:
            exe=Path(d)/"forged.exe";exe.write_bytes(b"fixture")
            data=Path(d)/"data";data.mkdir();(data/"existing").write_text("do not touch")
            with self.assertRaises(ValueError):offline_daemon_args(exe,data)
            with self.assertRaises(ValueError):offline_daemon_args(exe,Path(d)/"fresh",49581,49581,49582)
if __name__=="__main__":unittest.main()
