"""Adversarial interval scenarios; these tests exercise no real FRG proofs."""
from dataclasses import replace
import unittest

from continuity import Context, Window, assess_coverage


class ContinuityTests(unittest.TestCase):
    def setUp(self):
        self.context = Context("fixture-network", "draft", "miner-a", "bond-a",
                               "term-a", "history-a")

    def check(self, spans, expected):
        windows = tuple(Window(self.context, a, b) for a, b in spans)
        result = assess_coverage(windows, context=self.context, start=10, end=40)
        self.assertEqual(result.simulated_coverage, expected)
        self.assertFalse(result.binding_authority)

    def test_full_interval(self):
        self.check([(10, 40)], True)

    def test_adjacent_windows_in_any_order(self):
        self.check([(30, 40), (10, 20), (20, 30)], True)

    def test_overlap_and_duplicates_do_not_add_duration(self):
        self.check([(10, 25), (10, 25), (15, 30)], False)
        self.check([(10, 25), (15, 40)], True)

    def test_even_one_tick_gap_fails(self):
        self.check([(10, 20), (21, 40)], False)

    def test_recent_snapshot_does_not_establish_history(self):
        self.check([(39, 40)], False)

    def test_missing_beginning_or_end_fails(self):
        self.check([(11, 40)], False)
        self.check([(10, 39)], False)
        self.check([], False)

    def test_surrounding_coverage_is_sufficient(self):
        self.check([(0, 50)], True)

    def test_unrelated_intervals_do_not_fill_gap(self):
        self.check([(0, 10), (40, 50)], False)

    def test_context_replay_and_bond_replacement_fail(self):
        for field in vars(self.context):
            with self.subTest(field=field):
                changed = replace(self.context, **{field: "different"})
                result = assess_coverage(
                    (Window(self.context, 10, 20), Window(changed, 20, 40)),
                    context=self.context, start=10, end=40)
                self.assertFalse(result.simulated_coverage)
                self.assertEqual(result.reason, "context_mismatch")
                self.assertFalse(result.binding_authority)

    def test_reorg_invalidates_previously_complete_history(self):
        windows = (Window(self.context, 10, 40),)
        revised = replace(self.context, history_revision="post-reorg")
        result = assess_coverage(windows, context=revised, start=10, end=40)
        self.assertFalse(result.simulated_coverage)

    def test_invalid_intervals_are_not_snapshots(self):
        for a, b in [(10, 10), (20, 10), (-1, 40), (True, 40), (10, 40.0)]:
            with self.subTest(start=a, end=b), self.assertRaises(ValueError):
                Window(self.context, a, b)

    def test_invalid_context_and_container_rejected(self):
        with self.assertRaises(ValueError):
            replace(self.context, network=" ")
        with self.assertRaises(ValueError):
            assess_coverage([Window(self.context, 10, 40)],
                            context=self.context, start=10, end=40)


if __name__ == "__main__":
    unittest.main()
