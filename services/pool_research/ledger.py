"""Offline SQLite reward ledger prototype; NEVER sign or initiate payouts."""
import sqlite3
from contextlib import contextmanager
from .model import allocate_reward

class RewardLedger:
    def __init__(self, path):
        self.db=sqlite3.connect(path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS blocks(
          block_hash TEXT PRIMARY KEY, height INTEGER NOT NULL, reward INTEGER NOT NULL,
          maturity_height INTEGER NOT NULL, state TEXT NOT NULL CHECK(state IN ('immature','mature','orphaned'))
        );
        CREATE TABLE IF NOT EXISTS allocations(
          block_hash TEXT NOT NULL REFERENCES blocks(block_hash),
          miner TEXT NOT NULL, amount INTEGER NOT NULL CHECK(amount>=0),
          PRIMARY KEY(block_hash,miner)
        );
        CREATE TABLE IF NOT EXISTS fees(
          block_hash TEXT PRIMARY KEY REFERENCES blocks(block_hash), amount INTEGER NOT NULL
        );
        """)
        self.db.commit()

    def record_block(self, block_hash, height, reward_atomic, maturity_height, shares):
        """Record an independently verified canonical candidate only; no chain verification here."""
        if not isinstance(block_hash,str) or len(block_hash)!=64 or any(c not in '0123456789abcdef' for c in block_hash):
            raise ValueError("lowercase hexadecimal 32-byte block hash required")
        if type(height)!=int or height<0 or type(maturity_height)!=int or maturity_height<=height:
            raise ValueError("invalid height/maturity")
        alloc=allocate_reward(reward_atomic,shares)
        with self.db:
            old=self.db.execute("SELECT height,reward,maturity_height FROM blocks WHERE block_hash=?",(block_hash,)).fetchone()
            if old:
                if old!=(height,reward_atomic,maturity_height):
                    raise ValueError("block hash reuse with conflicting metadata")
                previous=dict(self.db.execute("SELECT miner,amount FROM allocations WHERE block_hash=?",(block_hash,)))
                fee=self.db.execute("SELECT amount FROM fees WHERE block_hash=?",(block_hash,)).fetchone()[0]
                if previous!=alloc.miner_atomic or fee!=alloc.fee_atomic:
                    raise ValueError("conflicting allocations")
                return False
            self.db.execute("INSERT INTO blocks VALUES (?,?,?,?,?)",(block_hash,height,reward_atomic,maturity_height,'immature'))
            self.db.execute("INSERT INTO fees VALUES (?,?)",(block_hash,alloc.fee_atomic))
            self.db.executemany("INSERT INTO allocations VALUES (?,?,?)",[(block_hash,k,v) for k,v in alloc.miner_atomic.items()])
        return True

    def reconcile_chain(self, canonical_hashes, tip_height):
        """Caller supplies canonical hashes from a verified node. No automatic payout authorization."""
        if type(tip_height)!=int or tip_height<0: raise ValueError("invalid tip")
        canonical=set(canonical_hashes)
        if any(not isinstance(h,str) or len(h)!=64 for h in canonical):
            raise ValueError("invalid canonical identifiers")
        with self.db:
            rows=self.db.execute("SELECT block_hash,maturity_height,state FROM blocks").fetchall()
            for hash_,maturity,state in rows:
                target='orphaned' if hash_ not in canonical else ('mature' if maturity<=tip_height else 'immature')
                # Intentionally reject automatic revival; requires operator investigation.
                if state=='orphaned' and target!='orphaned':
                    raise ValueError("orphan revival requires independent review")
                self.db.execute("UPDATE blocks SET state=? WHERE block_hash=?",(target,hash_))

    def balances(self):
        return dict(self.db.execute("""
          SELECT miner,SUM(amount) FROM allocations
          JOIN blocks USING (block_hash) WHERE state='mature'
          GROUP BY miner ORDER BY miner
        """))

    def close(self):
        self.db.close()
