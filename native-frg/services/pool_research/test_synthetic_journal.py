import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from .synthetic_journal import SyntheticJournal, JournalError


def record(**changes):
    values = dict(job="11"*16, nonce="01020304", session="22"*16,
                  digest="33"*32, difficulty=1, blob_sha256="44"*32, seed="55"*32)
    values.update(changes)
    return values


class JournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "checks.sqlite"
        self.journal = SyntheticJournal(self.path, max_records=2)

    def tearDown(self):
        self.journal.close()
        self.temp.cleanup()

    def test_reopen_idempotence_conflict_and_scope(self):
        self.journal.record(**record())
        self.journal.close()
        self.journal = SyntheticJournal(self.path)
        self.journal.record(**record())
        self.assertEqual(self.journal.count(), 1)
        with self.assertRaises(JournalError):
            self.journal.record(**record(digest="66"*32))
        self.assertEqual(self.journal.db.execute("SELECT synthetic,credited FROM checks").fetchall(), [(1, 0)])
        with self.assertRaises(sqlite3.IntegrityError):
            self.journal.db.execute("UPDATE checks SET credited=1")

    def test_capacity_is_transactional_and_duplicate_allowed(self):
        self.journal.record(**record())
        self.journal.record(**record(nonce="05060708"))
        with self.assertRaises(JournalError):
            self.journal.record(**record(nonce="090a0b0c"))
        self.journal.record(**record())
        self.assertEqual(self.journal.count(), 2)
        self.assertFalse(self.journal.db.in_transaction)

    def test_invalid_inputs_do_not_write(self):
        for field, value in (("nonce", "bad"), ("digest", "ff"),
                             ("session", "x"*32), ("difficulty", True),
                             ("difficulty", 0), ("seed", "FF"*32)):
            with self.assertRaises(JournalError):
                self.journal.record(**record(**{field: value}))
        self.assertEqual(self.journal.count(), 0)

    def test_unrelated_database_is_untouched(self):
        other = Path(self.temp.name) / "unrelated.sqlite"
        with sqlite3.connect(other) as db:
            db.execute("CREATE TABLE owner(value)")
            db.execute("INSERT INTO owner VALUES('preserve')")
        db.close()
        before = other.read_bytes()
        with self.assertRaises(JournalError):
            SyntheticJournal(other)
        self.assertEqual(before, other.read_bytes())

    def test_readonly_and_locked_storage_refuse_records(self):
        self.journal.db.execute("PRAGMA query_only=ON")
        with self.assertRaises(JournalError):
            self.journal.record(**record())
        self.journal.db.execute("PRAGMA query_only=OFF")
        other = sqlite3.connect(self.path, isolation_level=None)
        try:
            other.execute("BEGIN IMMEDIATE")
            with self.assertRaises(JournalError):
                self.journal.record(**record())
        finally:
            other.close()
        self.assertEqual(self.journal.count(), 0)
        self.journal.record(**record())

    def test_abrupt_exit_rolls_back_uncommitted_insert(self):
        self.journal.record(**record())
        self.journal.close()
        script = """import os,sqlite3,sys
db=sqlite3.connect(sys.argv[1],isolation_level=None)
db.execute('BEGIN IMMEDIATE')
db.execute("INSERT INTO checks SELECT job,'deadbeef',session,digest,difficulty,blob_sha256,seed,recorded_ns,synthetic,credited FROM checks LIMIT 1")
os._exit(0)
"""
        subprocess.run([sys.executable, "-c", script, str(self.path)], check=True, timeout=10)
        self.journal = SyntheticJournal(self.path)
        self.assertEqual(self.journal.count(), 1)
        self.assertEqual(self.journal.db.execute("PRAGMA integrity_check").fetchone()[0], "ok")


if __name__ == "__main__":
    unittest.main()
