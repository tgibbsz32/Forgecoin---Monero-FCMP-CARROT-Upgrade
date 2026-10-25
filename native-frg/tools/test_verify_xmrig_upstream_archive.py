"""Offline checksum-only unit tests; synthetic ZIP bytes are never unpacked."""
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tools.verify_xmrig_upstream_archive import ARCHIVE_NAME, inspect


class MinerArchiveTests(unittest.TestCase):
    def test_matching_synthetic_digest(self):
        with tempfile.TemporaryDirectory() as root:
            archive = Path(root) / ARCHIVE_NAME
            content = b"safe test fixture, not an executable"
            archive.write_bytes(content)
            expected = hashlib.sha256(content).hexdigest()
            ok, description = inspect(archive, expected_sha256=expected)
            self.assertTrue(ok, description)
            self.assertIn("checksum matches", description)
            self.assertEqual(archive.read_bytes(), content)

    def test_modified_archive_is_blocked(self):
        with tempfile.TemporaryDirectory() as root:
            archive = Path(root) / ARCHIVE_NAME
            archive.write_bytes(b"original")
            expected = hashlib.sha256(b"original").hexdigest()
            archive.write_bytes(b"modified")
            ok, description = inspect(archive, expected_sha256=expected)
            self.assertFalse(ok)
            self.assertIn("mismatch", description)

    def test_nonmatching_name_or_missing_file(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "untrusted.zip"
            path.write_bytes(b"arbitrary")
            self.assertFalse(inspect(path)[0])
            self.assertFalse(inspect(Path(root) / ARCHIVE_NAME)[0])

    def test_cli_denies_synthetic_untrusted_archive(self):
        with tempfile.TemporaryDirectory() as root:
            archive = Path(root) / ARCHIVE_NAME
            archive.write_bytes(b"fixture")
            script = Path(__file__).with_name("verify_xmrig_upstream_archive.py")
            process = subprocess.run([sys.executable, str(script),
                                      "--archive", str(archive)],
                                     capture_output=True, text=True, timeout=10)
            self.assertEqual(process.returncode, 1)
            self.assertIn("BLOCKED", process.stdout)
            self.assertIn("Do not run", process.stdout)


if __name__ == "__main__":
    unittest.main()
