"""Interval-coverage experiment on invented facts, NOT a native proof verifier.

No chain, cryptography, monitoring, identity, or authorization is implemented.
Ticks are abstract. A window asserts joint validity of ALL bond/mining gates
over a half-open interval; a balance snapshot cannot supply such a window.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Context:
    network: str
    policy: str
    entity: str
    bond: str
    term: str
    history_revision: str

    def __post_init__(self):
        if any(type(v) is not str or not v.strip() for v in vars(self).values()):
            raise ValueError("Nonempty synthetic context labels required")


@dataclass(frozen=True)
class Window:
    context: Context
    start: int
    end: int

    def __post_init__(self):
        if not isinstance(self.context, Context):
            raise ValueError("Synthetic context required")
        if (type(self.start) is not int or type(self.end) is not int
                or not 0 <= self.start < self.end):
            raise ValueError("A nonempty half-open interval is required")


@dataclass(frozen=True)
class Coverage:
    simulated_coverage: bool
    reason: str

    @property
    def binding_authority(self):
        return False


def assess_coverage(windows: tuple[Window, ...], *, context: Context,
                    start: int, end: int) -> Coverage:
    """Check coverage of [start, end) by same-context synthetic intervals.

The caller invents a history revision for one agreed canonical history, NOT
each successive tip. After reorg invalidation, old windows cannot be reused
without independent revalidation. Changing labels does not perform that work.
This is retrospective coverage only, never future lock or current eligibility.
"""
    Window(context, start, end)  # validate query using the same interval rules
    if type(windows) is not tuple or any(not isinstance(w, Window) for w in windows):
        raise ValueError("A tuple of synthetic windows is required")
    if any(w.context != context for w in windows):
        return Coverage(False, "context_mismatch")
    covered_until = start
    for window in sorted(windows, key=lambda w: (w.start, w.end)):
        if window.end <= covered_until:
            continue
        if window.start > covered_until:
            break
        covered_until = window.end
        if covered_until >= end:
            return Coverage(True, "synthetic_interval_covered")
    return Coverage(False, "uncovered_interval")
