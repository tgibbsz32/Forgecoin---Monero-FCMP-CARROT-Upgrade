"""Offline Solana escrow scenario tests: no wallet, network or live funds."""
from dataclasses import replace
import unittest
from services.atomic_swap_research.solana_escrow_sim import (
    AssetKind, Escrow, EscrowRejected, EscrowSpec, Stage,
    ORIGINAL_SPL_TOKEN_PROGRAM, request_real_solana_swap,
)


def spec(kind=AssetKind.SPL):
    return EscrowSpec(
        swap_id="test-001", owner="solana-maker", recipient="frg-taker",
        asset_kind=kind, asset_mint="TEST-USDC-MINT" if kind == AssetKind.SPL else None,
        amount_atomic=23_000_000, created_at=1000, t0=2000, t1=3000,
    )


class SolanaEscrowScenarioTests(unittest.TestCase):
    def test_original_spl_program_is_used_for_usdc(self):
        self.assertEqual(ORIGINAL_SPL_TOKEN_PROGRAM, "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
        self.assertEqual(spec().asset_kind, AssetKind.SPL)

    def test_sol_asset_requires_no_mint(self):
        self.assertIsNone(spec(AssetKind.SOL).asset_mint)
        with self.assertRaises(EscrowRejected):
            replace(spec(AssetKind.SOL), asset_mint="wrong")

    def test_invalid_pair_data_fails_closed(self):
        s = spec()
        for patch in (
            {"amount_atomic": 0}, {"amount_atomic": -1},
            {"amount_atomic": 2**64}, {"amount_atomic": 0.5},
            {"asset_mint": None}, {"t0": 3000}, {"t1": 2000},
            {"owner": s.recipient}, {"asset_kind": "ERC20"},
        ):
            with self.subTest(patch=patch), self.assertRaises(EscrowRejected):
                replace(s, **patch)

    def test_ready_requires_lock_confirmation(self):
        e = Escrow(spec())
        with self.assertRaises(EscrowRejected):
            e.ready("solana-maker", 1100, remote_lock_confirmed=False)
        with self.assertRaises(EscrowRejected):
            e.ready("other", 1100, remote_lock_confirmed=True)
        e.ready("solana-maker", 1100, remote_lock_confirmed=True)
        self.assertEqual(e.stage, Stage.READY)

    def test_claim_after_ready_then_cannot_refund(self):
        e = Escrow(spec())
        e.ready("solana-maker", 1100, remote_lock_confirmed=True)
        with self.assertRaises(EscrowRejected):
            e.claim("frg-taker", 1101, secret_proof_verified=False)
        e.claim("frg-taker", 1101, secret_proof_verified=True)
        self.assertEqual(e.stage, Stage.CLAIMED)
        with self.assertRaises(EscrowRejected):
            e.refund("solana-maker", 3000, refund_proof_verified=True)

    def test_claim_after_first_timeout_without_ready(self):
        e = Escrow(spec(AssetKind.SOL))
        with self.assertRaises(EscrowRejected):
            e.claim("frg-taker", 1999, secret_proof_verified=True)
        e.claim("frg-taker", 2000, secret_proof_verified=True)
        self.assertEqual(e.stage, Stage.CLAIMED)

    def test_refund_before_first_timeout_if_not_ready(self):
        e = Escrow(spec())
        e.refund("solana-maker", 1200, refund_proof_verified=True)
        self.assertEqual(e.stage, Stage.REFUNDED)
        with self.assertRaises(EscrowRejected):
            e.claim("frg-taker", 2200, secret_proof_verified=True)

    def test_claim_refund_window_mutually_exclusive(self):
        for ready in (False, True):
            e = Escrow(spec())
            if ready:
                e.ready("solana-maker", 1100, remote_lock_confirmed=True)
            with self.subTest(ready=ready), self.assertRaises(EscrowRejected):
                e.refund("solana-maker", 2500, refund_proof_verified=True)
            with self.subTest(ready=ready), self.assertRaises(EscrowRejected):
                e.claim("frg-taker", 3000, secret_proof_verified=True)
            e.refund("solana-maker", 3000, refund_proof_verified=True)
            self.assertEqual(e.stage, Stage.REFUNDED)

    def test_claimed_can_never_become_refunded(self):
        e = Escrow(spec())
        e.claim("frg-taker", 2200, secret_proof_verified=True)
        with self.assertRaises(EscrowRejected):
            e.refund("solana-maker", 3100, refund_proof_verified=True)

    def test_real_operations_blocked(self):
        with self.assertRaises(NotImplementedError):
            request_real_solana_swap()


if __name__ == "__main__":
    unittest.main()
