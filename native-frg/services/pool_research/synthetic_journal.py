"""Bounded SQLite evidence records. Synthetic checks only; no balances/credits.

Use a private research directory. This is not a hostile-filesystem boundary,
tamper-proof log, production share ledger or payout authority.
"""
from pathlib import Path
import re
import sqlite3
import time

APPLICATION_ID = 0x46524753


class JournalError(ValueError):
    pass


class SyntheticJournal:
    def __init__(self, path, *, max_records=10000):
        if type(max_records) is not int or not 1 <= max_records <= 10000:
            raise ValueError("invalid journal limit")
        self.max_records = max_records
        self.db = None
        try:
            self.db = sqlite3.connect(Path(path), timeout=0.1, isolation_level=None)
            app = self.db.execute("PRAGMA application_id").fetchone()[0]
            version = self.db.execute("PRAGMA user_version").fetchone()[0]
            tables = self.db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
            if (app, version) != (APPLICATION_ID, 1):
                if app or version or tables:
                    raise JournalError("not a synthetic verification journal")
                self.db.executescript(f"""
                    BEGIN IMMEDIATE;
                    CREATE TABLE checks (
                        job TEXT NOT NULL, nonce TEXT NOT NULL,
                        session TEXT NOT NULL, digest TEXT NOT NULL,
                        difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 4294967295),
                        blob_sha256 TEXT NOT NULL, seed TEXT NOT NULL,
                        recorded_ns INTEGER NOT NULL,
                        synthetic INTEGER NOT NULL DEFAULT 1 CHECK(synthetic=1),
                        credited INTEGER NOT NULL DEFAULT 0 CHECK(credited=0),
                        PRIMARY KEY(job,nonce)
                    );
                    PRAGMA application_id={APPLICATION_ID};
                    PRAGMA user_version=1;
                    COMMIT;
                """)
            self.db.execute("PRAGMA journal_mode=DELETE")
            self.db.execute("PRAGMA synchronous=FULL")
            # Hard SQLite page ceiling supplements the record-count bound.
            self.db.execute("PRAGMA max_page_count=16384")
            self.db.execute("SELECT job,nonce,session,digest,difficulty,blob_sha256,seed,recorded_ns,synthetic,credited FROM checks LIMIT 0")
        except (sqlite3.Error, OSError, JournalError) as error:
            self.close()
            raise JournalError("journal could not be opened") from error

    def close(self):
        if self.db is not None:
            self.db.close()
            self.db = None

    def record(self, *, job, nonce, session, digest, difficulty, blob_sha256, seed):
        fields = (job, nonce, session, digest, blob_sha256, seed)
        for value, width in zip(fields, (32, 8, 32, 64, 64, 64)):
            if not isinstance(value, str) or not re.fullmatch(f"[0-9a-f]{{{width}}}", value):
                raise JournalError("invalid verification record")
        if type(difficulty) is not int or not 1 <= difficulty <= 0xffffffff:
            raise JournalError("invalid verification difficulty")
        if self.db is None:
            raise JournalError("journal is closed")
        values = (session, digest, difficulty, blob_sha256, seed)
        try:
            self.db.execute("BEGIN IMMEDIATE")
            existing = self.db.execute(
                "SELECT session,digest,difficulty,blob_sha256,seed FROM checks WHERE job=? AND nonce=?",
                (job, nonce)).fetchone()
            if existing is not None:
                if existing != values:
                    raise JournalError("conflicting verification record")
            else:
                count = self.db.execute("SELECT count(*) FROM checks").fetchone()[0]
                if count >= self.max_records:
                    raise JournalError("verification journal capacity reached")
                self.db.execute(
                    "INSERT INTO checks(job,nonce,session,digest,difficulty,blob_sha256,seed,recorded_ns) VALUES(?,?,?,?,?,?,?,?)",
                    (job, nonce, *values, time.time_ns()))
            self.db.execute("COMMIT")
        except (sqlite3.Error, JournalError) as error:
            if self.db.in_transaction:
                try:
                    self.db.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
            raise JournalError("verification record unavailable") from error

    def count(self):
        if self.db is None:
            raise JournalError("journal is closed")
        return self.db.execute("SELECT count(*) FROM checks").fetchone()[0]
