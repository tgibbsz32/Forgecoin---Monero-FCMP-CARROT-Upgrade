"""Adversarial synthetic scenarios; no real coins, keys, or network access."""
from dataclasses import replace
import unittest

from research.governance_bonds.model import Fixture, Policy, simulate


class BondPolicyTests(unittest.TestCase):
    def setUp(self):
        self.policy = Policy(100, 30, 5, 2, 10)
        self.fixture = Fixture(
            entity="miner-a", bond="output-a", mining_claim="work-a",
            network="synthetic-frg", anchor="agreed-tip", reviewed_at=100,
            continuous_since=70, mining_valid_until=110, earliest_spend=210,
            term_end=200, amount_atomic=100,
            reviewers=frozenset({"reviewer-a", "reviewer-b"}),
            conflicts=frozenset(), mining_verified=True, lock_enforced=True,
            ownership_verified=True, unspent_verified=True,
            uniqueness_verified=True, continuity_verified=True)

    def run_case(self, fixture=None, **kwargs):
        fixture = fixture or self.fixture
        context = dict(policy=self.policy, now=100, network="synthetic-frg",
                       anchor="agreed-tip", cohort=(fixture,))
        context.update(kwargs)
        return simulate(fixture, **context)

    def test_qualified_fixture_only_reaches_review_never_authority(self):
        for seated in (False, True):
            result = self.run_case(seated=seated)
            self.assertEqual(result.simulated_state, "candidate_for_review")
            self.assertFalse(result.binding_authority)

    def test_each_independent_requirement_fails_closed(self):
        for field in ("mining_verified", "lock_enforced", "ownership_verified",
                      "unspent_verified", "uniqueness_verified", "continuity_verified"):
            for value in (False, None, "true", 1):
                with self.subTest(field=field, value=value):
                    result = self.run_case(replace(self.fixture, **{field: value}), seated=True)
                    self.assertEqual(result.simulated_state, "suspended")
                    self.assertFalse(result.binding_authority)

    def test_balance_statement_and_buyer_do_not_qualify(self):
        for field in ("lock_enforced", "mining_verified"):
            result = self.run_case(replace(self.fixture, **{field: False, "amount_atomic": 10**12}))
            self.assertEqual(result.simulated_state, "ineligible")

    def test_qualification_boundary_and_restart(self):
        self.assertEqual(self.run_case(replace(self.fixture, continuous_since=71)).simulated_state, "qualifying")
        self.assertEqual(self.run_case().simulated_state, "candidate_for_review")
        self.assertEqual(self.run_case(replace(self.fixture, continuous_since=100), seated=True).simulated_state, "suspended")

    def test_reorg_wrong_network_and_stale_reviews_suspend(self):
        for change in ({"anchor": "orphaned"}, {"network": "solana"},
                       {"reviewed_at": 94}, {"reviewed_at": 101},
                       {"continuous_since": 101}):
            with self.subTest(change=change):
                self.assertEqual(self.run_case(replace(self.fixture, **change), seated=True).simulated_state, "suspended")
        self.assertEqual(self.run_case(replace(self.fixture, reviewed_at=95)).simulated_state, "candidate_for_review")

    def test_expiry_withdrawal_spending_and_revocation_suspend(self):
        for change in ({"mining_valid_until": 100}, {"earliest_spend": 100},
                       {"earliest_spend": 209}, {"term_end": 100},
                       {"amount_atomic": 99}, {"unbond_requested": True},
                       {"revoked": True}, {"unspent_verified": False}):
            with self.subTest(change=change):
                self.assertEqual(self.run_case(replace(self.fixture, **change), seated=True).simulated_state, "suspended")

    def test_conflicts_and_duplicate_reviewers_cannot_make_quorum(self):
        for change in ({"reviewers": frozenset({"reviewer-a", "reviewer-a"})},
                       {"reviewers": frozenset({"miner-a", "reviewer-a"})},
                       {"conflicts": frozenset({"reviewer-a"})},
                       {"reviewers": frozenset({"", "reviewer-a"})}):
            result = self.run_case(replace(self.fixture, **change))
            self.assertEqual(result.simulated_state, "ineligible")
            self.assertTrue(set(result.reasons) & {"independent_quorum_missing", "invalid_reviewers"})

    def test_duplicate_entity_bond_and_pool_work_reject_both_claimants(self):
        other = replace(self.fixture, entity="miner-b", bond="output-b", mining_claim="work-b")
        for field in ("entity", "bond", "mining_claim"):
            duplicate = replace(other, **{field: getattr(self.fixture, field)})
            cohort = (self.fixture, duplicate)
            for item in cohort:
                with self.subTest(field=field, entity=item.entity):
                    self.assertIn("duplicate_" + field, self.run_case(item, cohort=cohort).reasons)

    def test_missing_context_and_cohort_fail_closed(self):
        for change in ({"cohort": ()}, {"anchor": ""}, {"network": ""}):
            self.assertEqual(self.run_case(**change).simulated_state, "ineligible")

    def test_policy_and_amounts_require_exact_integers(self):
        for value in (0, -1, True, 1.5, "100"):
            with self.assertRaises(ValueError):
                Policy(value, 30, 5, 2, 10)
        for value in (-1, True, 1.5, "100"):
            self.assertEqual(self.run_case(replace(self.fixture, amount_atomic=value)).simulated_state, "ineligible")

    def test_extra_bond_does_not_buy_extra_authority(self):
        self.assertEqual(self.run_case(), self.run_case(replace(self.fixture, amount_atomic=10**12)))


if __name__ == "__main__":
    unittest.main()
