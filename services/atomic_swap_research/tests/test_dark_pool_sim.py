"""Tests for offline settlement *previews*, not actual chain settlement."""
import unittest

from services.atomic_swap_research.dark_pool_sim import (
    OrderIntent, ProductionIntegrationBlocked, RejectedOrder,
    ThresholdVaultPolicy, order_commitment, preview_exact_match,
    request_blind_relay, request_custodial_settlement,
)


def offers():
    sell = OrderIntent(
        "seller-001", "party-A", "SELL_BASE", "FRG", "USDC",
        100_000_000, 250_000_000, 1800000200, "salt-A-unique"
    )
    buy = OrderIntent(
        "buyer-001", "party-B", "BUY_BASE", "FRG", "USDC",
        100_000_000, 250_000_000, 1800000200, "salt-B-unique"
    )
    return sell, buy


class DarkPoolSimulationTests(unittest.TestCase):
    def test_matched_rfq_conserves_base_and_quote_with_fee(self):
        sell, buy = offers()
        p = preview_exact_match(sell, buy, now=1800000000, fee_bps=20)
        self.assertEqual(p.fee_units, 500_000)
        self.assertEqual(p.seller_quote_receives, 249_500_000)
        self.assertEqual(p.buyer_base_delta + p.seller_base_delta, 0)
        self.assertEqual(
            p.buyer_quote_delta + p.seller_quote_delta + p.treasury_quote_delta, 0
        )

    def test_zero_fee(self):
        sell, buy = offers()
        p = preview_exact_match(sell, buy, now=1800000000, fee_bps=0)
        self.assertEqual(p.fee_units, 0)
        self.assertEqual(p.seller_quote_receives, 250_000_000)

    def test_fee_rounds_up_and_below_proceeds(self):
        sell = OrderIntent("s", "a", "SELL_BASE", "FRG", "USDC", 1, 10, 10, "x")
        buy = OrderIntent("b", "b", "BUY_BASE", "FRG", "USDC", 1, 10, 10, "y")
        self.assertEqual(preview_exact_match(sell, buy, now=0, fee_bps=1).fee_units, 1)
        with self.assertRaises(RejectedOrder):
            preview_exact_match(sell, buy, now=0, fee_bps=9999)

    def test_rejects_self_trade(self):
        sell, buy = offers()
        buy = OrderIntent("b", "party-A", "BUY_BASE", "FRG", "USDC",
                          100_000_000, 250_000_000, 1800000200, "another")
        with self.assertRaisesRegex(RejectedOrder, "self"):
            preview_exact_match(sell, buy, now=1800000000, fee_bps=10)

    def test_rejects_wrong_price(self):
        sell, buy = offers()
        buy = OrderIntent("b", "party-B", "BUY_BASE", "FRG", "USDC",
                          100_000_000, 240_000_000, 1800000200, "another")
        with self.assertRaisesRegex(RejectedOrder, "match"):
            preview_exact_match(sell, buy, now=1800000000, fee_bps=10)

    def test_rejects_expiry(self):
        sell, buy = offers()
        with self.assertRaisesRegex(RejectedOrder, "expired"):
            preview_exact_match(sell, buy, now=1800000200, fee_bps=10)

    def test_rejects_duplicate_nonce(self):
        sell, buy = offers()
        buy = OrderIntent("b", "party-B", "BUY_BASE", "FRG", "USDC",
                          100_000_000, 250_000_000, 1800000200, sell.nonce)
        with self.assertRaisesRegex(RejectedOrder, "nonce"):
            preview_exact_match(sell, buy, now=1800000000, fee_bps=10)

    def test_rejects_invalid_amounts_and_fee_policy(self):
        sell, buy = offers()
        for bad in (0, -1, 0.1, True):
            with self.subTest(bad=bad):
                candidate = OrderIntent("s", "party-A", "SELL_BASE", "FRG", "USDC",
                                        bad, 10, 1800000200, "x")
                with self.assertRaises(RejectedOrder):
                    preview_exact_match(candidate, buy, now=1800000000, fee_bps=5)
        for fee in (-1, 10000, 0.5, True):
            with self.subTest(fee=fee), self.assertRaises(RejectedOrder):
                preview_exact_match(sell, buy, now=1800000000, fee_bps=fee)

    def test_signer_roster_is_not_tss_signing(self):
        p = ThresholdVaultPolicy("vault-lab", "ethereum-sepolia", ("s1", "s2", "s3"), 2)
        self.assertTrue(p.check_declared_quorum(("s1", "s2")))
        self.assertFalse(p.check_declared_quorum(("s1",)))
        self.assertFalse(p.check_declared_quorum(("s1", "s1")))
        self.assertFalse(p.check_declared_quorum(("s1", "attacker")))
        with self.assertRaises(RejectedOrder):
            ThresholdVaultPolicy("vault-lab", "ethereum", ("s1", "s1"), 2)

    def test_hash_commitment_is_only_a_demo(self):
        sell, buy = offers()
        self.assertNotEqual(order_commitment(sell), order_commitment(buy))
        twin = OrderIntent(sell.order_id, sell.participant, sell.side,
                           sell.base_asset, sell.quote_asset, sell.base_units,
                           sell.quote_units, sell.expires_at, "different salt")
        self.assertNotEqual(order_commitment(sell), order_commitment(twin))

    def test_all_real_operations_are_fail_closed(self):
        with self.assertRaises(ProductionIntegrationBlocked):
            request_custodial_settlement()
        with self.assertRaises(ProductionIntegrationBlocked):
            request_blind_relay()


if __name__ == "__main__":
    unittest.main()
