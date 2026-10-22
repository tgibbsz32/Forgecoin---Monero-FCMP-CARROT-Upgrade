"""Synthetic policy experiment. NOT a verifier, registry, or voting service.

All facts, including reviewer independence and lock enforcement, are invented
test inputs. Never pass wallet evidence here or use results to grant authority.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Policy:
    minimum_atomic: int
    qualification_ticks: int
    review_max_age: int
    reviewer_quorum: int
    cooldown_ticks: int

    def __post_init__(self):
        for value in vars(self).values():
            if type(value) is not int or value <= 0:
                raise ValueError("Explicit positive integer experiment parameters required")


@dataclass(frozen=True)
class Fixture:
    entity: str
    bond: str
    mining_claim: str
    network: str
    anchor: str
    reviewed_at: int
    continuous_since: int
    mining_valid_until: int
    earliest_spend: int
    term_end: int
    amount_atomic: int
    reviewers: frozenset[str]
    conflicts: frozenset[str]
    mining_verified: bool = False
    lock_enforced: bool = False
    ownership_verified: bool = False
    unspent_verified: bool = False
    uniqueness_verified: bool = False
    continuity_verified: bool = False
    unbond_requested: bool = False
    revoked: bool = False


@dataclass(frozen=True)
class Result:
    simulated_state: str
    reasons: tuple[str, ...]

    @property
    def binding_authority(self):
        return False


def simulate(fixture: Fixture, *, policy: Policy, now: int, network: str,
             anchor: str, cohort: tuple[Fixture, ...], seated: bool = False) -> Result:
    """Evaluate a complete synthetic snapshot; no I/O or persistent state.

The coordinator supplies a common independently agreed chain anchor and the
entire cohort, not just approved applicants. Ticks are abstract, not block
heights or wall time. `seated` means an imaginary incumbent in the experiment.
    """
    if type(now) is not int or now < 0 or type(seated) is not bool:
        raise ValueError("Invalid experiment context")
    reasons = []
    if not network or not anchor:
        reasons.append("missing_context")
    if any(type(v) is not str or not v for v in (
            fixture.entity, fixture.bond, fixture.mining_claim,
            fixture.network, fixture.anchor)):
        reasons.append("missing_identifiers")
    numeric = (fixture.reviewed_at, fixture.continuous_since,
               fixture.mining_valid_until, fixture.earliest_spend,
               fixture.term_end, fixture.amount_atomic)
    if any(type(v) is not int or v < 0 for v in numeric):
        return Result("suspended" if seated else "ineligible", ("invalid_numbers",))
    if fixture.network != network or fixture.anchor != anchor:
        reasons.append("chain_disagreement")
    if not fixture.continuous_since <= fixture.reviewed_at <= now:
        reasons.append("invalid_chronology")
    if now - fixture.reviewed_at > policy.review_max_age:
        reasons.append("stale_review")
    if fixture.mining_valid_until <= now:
        reasons.append("mining_expired")
    if fixture.term_end <= now:
        reasons.append("term_ended")
    if fixture.earliest_spend <= now or fixture.earliest_spend < fixture.term_end + policy.cooldown_ticks:
        reasons.append("insufficient_lock_horizon")
    if fixture.amount_atomic < policy.minimum_atomic:
        reasons.append("insufficient_bond")
    for field in ("mining_verified", "lock_enforced", "ownership_verified",
                  "unspent_verified", "uniqueness_verified", "continuity_verified"):
        if getattr(fixture, field) is not True:
            reasons.append(field + "_missing")
    if fixture.unbond_requested is not False or fixture.revoked is not False:
        reasons.append("withdrawn_or_revoked")
    # Distinct strings merely MODEL independently controlled organizations.
    # A real implementation needs an independently governed reviewer registry.
    if (type(fixture.reviewers) is not frozenset or
            type(fixture.conflicts) is not frozenset or
            any(type(v) is not str or not v for v in fixture.reviewers | fixture.conflicts)):
        reasons.append("invalid_reviewers")
    elif len(fixture.reviewers - fixture.conflicts - {fixture.entity}) < policy.reviewer_quorum:
        reasons.append("independent_quorum_missing")
    if fixture not in cohort:
        reasons.append("missing_cohort_record")
    for field in ("entity", "bond", "mining_claim"):
        if sum(getattr(item, field) == getattr(fixture, field) for item in cohort) != 1:
            reasons.append("duplicate_" + field)
    if reasons:
        return Result("suspended" if seated else "ineligible", tuple(reasons))
    if now - fixture.continuous_since < policy.qualification_ticks:
        return Result("suspended" if seated else "qualifying", ("qualification_incomplete",))
    # This never seats anyone, enables ballots, or changes registry roles.
    return Result("candidate_for_review", ())
