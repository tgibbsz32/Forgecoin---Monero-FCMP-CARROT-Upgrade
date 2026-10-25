"""Offline synthetic PE fixtures; no fixture is executed."""
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools.preflight_desktop_mining import inspect


def fixture():
    data = bytearray(512)
    data[:2] = b'MZ'
    struct.pack_into('<I', data, 60, 64)
    data[64:68] = b'PE\0\0'
    struct.pack_into('<HHIIIHH', data, 68, 0x8664, 1, 0, 0, 0, 112, 2)
    struct.pack_into('<H', data, 88, 0x20b)
    struct.pack_into('<II', data, 216, 16, 256)
    return data


class PreflightTests(unittest.TestCase):
    def test_structural_rejections(self):
        cases = [b'', b'MZ', bytes(64)]
        for offset, fmt, value in [(60, '<I', 0xffffffff), (64, '<I', 0),
                (68, '<H', 0x14c), (70, '<H', 0), (70, '<H', 97),
                (84, '<H', 111), (84, '<H', 600), (86, '<H', 0),
                (86, '<H', 0x2002), (88, '<H', 0x10b),
                (216, '<I', 999), (220, '<I', 0)]:
            data = fixture()
            struct.pack_into(fmt, data, offset, value)
            cases.append(data)
        cases.append(fixture()[:239])
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'synthetic.exe'
            for i, data in enumerate(cases):
                with self.subTest(case=i):
                    path.write_bytes(data)
                    self.assertTrue(inspect(path, 'daemon').startswith('BLOCKED'))

    def test_hash_and_read_only(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'synthetic.exe'
            data = fixture()
            path.write_bytes(data)
            result = inspect(path, 'daemon')
            self.assertIn(hashlib.sha256(data).hexdigest(), result)
            self.assertIn('provenance unverified', result)
            self.assertEqual(path.read_bytes(), data)

    def test_absent_and_unreadable(self):
        self.assertTrue(inspect(None, 'daemon').startswith('BLOCKED'))
        with tempfile.TemporaryDirectory() as root:
            for path in [Path(root), Path(root) / 'absent.exe']:
                self.assertTrue(inspect(path, 'daemon').startswith('BLOCKED'))
        with patch.object(Path, 'open', side_effect=PermissionError):
            self.assertTrue(inspect('denied.exe', 'daemon').startswith('BLOCKED'))

    def test_cli_missing_and_success(self):
        script = str(Path(__file__).with_name('preflight_desktop_mining.py'))
        result = subprocess.run([sys.executable, script], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.count('BLOCKED'), 4)
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / 'synthetic.exe'
            path.write_bytes(fixture())
            args = [item for name in ['desktop', 'daemon', 'wallet-rpc', 'xmrig']
                    for item in ['--' + name, str(path)]]
            result = subprocess.run([sys.executable, script, *args], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertIn('functional Solo/Pool tests still required', result.stdout)

if __name__ == '__main__':
    unittest.main()
