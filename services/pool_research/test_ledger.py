"""Deterministic offline ledger safety checks; no native daemon involved."""
import tempfile
import unittest
from pathlib import Path
from services.pool_research.ledger import RewardLedger

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.dir=tempfile.TemporaryDirectory()
        self.path=Path(self.dir.name)/"pool.sqlite"
        self.ledger=RewardLedger(self.path)
        self.h="ab"*32
        self.shares={"minerA":3,"minerB":1}
    def tearDown(self):
        self.ledger.close()
        self.dir.cleanup()
    def test_maturity_idempotence_and_persistence(self):
        self.assertTrue(self.ledger.record_block(self.h,100,10000,160,self.shares))
        self.assertFalse(self.ledger.record_block(self.h,100,10000,160,self.shares))
        self.ledger.reconcile_chain([self.h],159)
        self.assertEqual(self.ledger.balances(),{})
        self.ledger.close()
        self.ledger=RewardLedger(self.path)
        self.ledger.reconcile_chain([self.h],160)
        self.assertEqual(self.ledger.balances(),{"minerA":7425,"minerB":2475})
    def test_orphan_reversal_and_no_automatic_revival(self):
        self.ledger.record_block(self.h,100,10000,160,self.shares)
        self.ledger.reconcile_chain([self.h],160)
        self.ledger.reconcile_chain([],161)
        self.assertEqual(self.ledger.balances(),{})
        with self.assertRaisesRegex(ValueError,"revival"):
            self.ledger.reconcile_chain([self.h],162)
    def test_conflicting_duplicate_rejected(self):
        self.ledger.record_block(self.h,100,10000,160,self.shares)
        with self.assertRaisesRegex(ValueError,"conflicting"):
            self.ledger.record_block(self.h,100,10000,160,{"minerA":1})
    def test_invalid_inputs(self):
        for args in [("bad",100,10000,160,self.shares),(self.h,-1,10000,160,self.shares),(self.h,100,10000,100,self.shares)]:
            with self.assertRaises(ValueError):self.ledger.record_block(*args)
if __name__=="__main__":
    unittest.main()
