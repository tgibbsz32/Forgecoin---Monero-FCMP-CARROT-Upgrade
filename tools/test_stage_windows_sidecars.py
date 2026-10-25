import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools import stage_windows_sidecars as staging


class StagingTests(unittest.TestCase):
    def test_rejects_complete_set_before_writing(self):
        with tempfile.TemporaryDirectory() as root:
            source, dest = Path(root) / "src", Path(root) / "dest"
            source.mkdir()
            (source / "a.exe").write_bytes(b"reviewed")
            (source / "b.exe").write_bytes(b"tampered")
            with patch.object(staging, "REVIEWED", dict.fromkeys(
                    ["a", "b"], hashlib.sha256(b"reviewed").hexdigest())):
                with self.assertRaises(ValueError):
                    staging.stage(source, dest)
            self.assertFalse(dest.exists())

    def test_stages_exact_bytes_and_detects_later_replacement(self):
        with tempfile.TemporaryDirectory() as root:
            source, dest = Path(root) / "src", Path(root) / "dest"
            source.mkdir()
            (source / "a.exe").write_bytes(b"reviewed")
            with patch.object(staging, "REVIEWED", {
                    "a": hashlib.sha256(b"reviewed").hexdigest()}):
                staging.stage(source, dest)
                self.assertEqual(staging.validated(dest, True), {"a": b"reviewed"})
                (dest / f"a-{staging.TARGET}.exe").write_bytes(b"replacement")
                with self.assertRaises(ValueError):
                    staging.validated(dest, True)


if __name__ == "__main__":
    unittest.main()
