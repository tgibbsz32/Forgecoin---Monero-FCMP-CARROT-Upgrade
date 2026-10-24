# Native FRG miner governance bonds — research proposal

Status: development-stage proposal, not ratified. No real funds, production
voting, native lock changes, staking yield or proof-of-stake consensus.
The [charter](../../governance-charter.md) and [roadmap](../../ROADMAP.md)
remain authoritative for project scope. V1 is native FRG only. Mining-linked
secondary token issuance and Solana staking remain deferred historical ideas; this
proposal neither implements nor reauthorizes them.

## Decision proposed

A miner representative would retain authority only while BOTH independently
verified native mining participation AND a continuously qualified, enforceable
native FRG bond remain valid. Buying FRG, a wallet signature, a balance proof,
a pool operator's assertion, or a database approval alone is insufficient.
Bond size is a qualification threshold, never extra votes or consensus weight.
This concerns representative eligibility; ordinary mining needs no bond.
Elector eligibility, chamber seats, quorum and constituency balance remain
separate unresolved constitutional decisions. No automatic founder seats or
miner majority follows from this design.

## Verification boundary (not implemented)

An eventual verifier must bind each evidence bundle to a policy version,
native network/genesis identity, agreed chain checkpoint/hash, entity credential,
unique bond/output commitment, mining contribution claim, representative term,
expiry and replay-resistant challenge. Reviewers must attest to the same bundle.
Evidence revisions invalidate prior attestations. A real deployment needs
authenticated independent reviewers, a conflict registry and reviewed quorum;
multiple keys or names belonging to one operator count once. The applicant,
their pool operator and related entities cannot form an independent quorum.

For solo mining, validate canonical accepted block work and a privacy-reviewed
link to the claimant's mining contribution/control. Receipt of FRG is not proof
of mining. For pool participants, require independently corroborated share/work
records tied to the participant and canonical payout accounting, with challenge
and audit procedures. A pool signature alone is insufficient. Specify how pool
and worker claims partition contribution so neither can double-count the same
work. Do not require public release of unrelated wallet history. If independent
pool attribution is infeasible, that path remains unavailable, not self-certified.

For the bond, separately establish native asset, amount in integer atomic units,
control, uniqueness, canonical inclusion, adequate confirmations, unspent status
and the earliest enforceable spend boundary. The lock must cover the entire term
plus reviewed cooldown, accounting for consensus unlock leeway. A pledge not to
spend, wallet-local freeze, ordinary signed balance or custody promise is not a
native enforceable bond. Private amounts, ring membership and key images make
ownership, amount, non-spend and uniqueness proofs a security/privacy research
problem. No proof scheme is selected by this proposal.

### Native feasibility observations

At the reviewed source baseline from PR #9:

- `src/cryptonote_core/cryptonote_tx_utils.cpp`,
  `construct_tx_with_tx_key`, initializes ordinary transaction `unlock_time` to 0.
- `src/wallet/wallet2.cpp` rejects nonzero construction unlock time in its
  transaction sanity check and builds ordinary transaction data with zero.
- `src/cryptonote_core/blockchain.cpp`, `is_tx_spendtime_unlocked`, contains
  height/time checks with allowed deltas; coinbase maturity has separate rules.

These observations do NOT demonstrate a usable governance-bond construction or
safe end-to-end enforcement. Do not bypass wallet checks, expose a lock RPC or
patch native transaction construction based on this document. A separate
reviewed feasibility study must test consensus acceptance, wallet recovery,
earliest-spend semantics, reorgs and privacy on isolated synthetic/regtest data.
Do not infer wall-clock lock duration from expected block intervals. If the
existing protocol cannot safely support the required proofs and lock semantics,
binding miner authority stays disabled pending a separately reviewed proposal.

## Proposed lifecycle and continuity

| Situation | Proposed treatment |
| --- | --- |
| New complete evidence | Independently review; begin qualification only from verifiable continuous validity |
| Qualification incomplete | No representative authority |
| Both requirements valid for the full period | Candidate for independent selection/review; never automatic seating |
| Seated representative | Recheck both requirements before each authority-bearing action and on evidence/chain changes |
| Stale/unavailable verifier, checkpoint disagreement or reorg | Suspend authority immediately; preserve audit trail and revalidate canonical evidence |
| Mining expires, lock expires, bond spent/revoked, withdrawal requested | Suspend immediately; cooldown never preserves voting rights |
| Duplicate entity, reused bond or overlapping work claim | Hold all affected claims for independent resolution; never first-writer-wins |
| Successful appeal or replacement bond | Independent re-review; no silent restoration; restart qualification after any unproven gap |
| Term ends, key loss or voluntary departure | Remove authority; apply reviewed vacancy/replacement procedure |

A fresh snapshot alone cannot prove continuity. Reviewers need a verifiable
history spanning the qualification interval, with any uncovered interval failing
closed. Reorg rollback must invalidate orphaned facts and their qualification
history. A reviewed protocol must define confirmation depth, monitoring outage
limits, mining activity windows, and whether preserved canonical history permits
requalification without restarting. Administrative appeal cannot waive the bond
or mining requirement. Past valid ballots are not rewritten automatically;
fraud discoveries require a separately ratified dispute procedure.

Unbond requests suspend authority before any release becomes possible. This
proposal does not release or confiscate funds: actual spendability belongs to
native consensus. No slashing, automatic transfers, emergency unlock or key
recovery mechanism is introduced. Publish withdrawal limits before any deposits.

## Synthetic model and tests

The [private proof and continuity review](PRIVATE_CONTINUITY_REVIEW.md) examines
the existing reserve-proof disclosure boundary and native relay restrictions at
a pinned revision. Its separate `continuity.py` experiment tests synthetic
interval coverage, including gaps, replacement and reorg invalidation. It does
not turn balance snapshots into proofs or change the snapshot model below.

`model.py` is a pure in-memory policy experiment, isolated from governance API,
registry, elections, wallet and daemon. It has no routes, database, signatures,
network calls, addresses or transaction construction. All input attestations
are invented fixture facts, **not verified evidence**. Reviewer identifiers do
not establish real independence; a cohort supplied by a caller cannot establish
global uniqueness. The model assumes a complete cohort and agreed chain context.
Each synthetic mining claim names a nonempty set of work units. Overlapping sets
hold both claimants even when their claim IDs differ; disjoint pool work can be
reviewed separately. Missing or malformed work records invalidate the snapshot.
Real work-unit identifiers and non-overlap proofs are not designed here: caller
chosen labels cannot detect renamed, concealed or falsely attributed work. This
conservative experiment also cannot adjudicate legitimate shared contributions.
It does not implement a proof verifier, continuity monitor, appeal registry,
election system or persistent state machine. Never adapt it directly into an
authorization endpoint.

All outputs have `binding_authority == False`. Even a fully passing fixture is
only `candidate_for_review`. `seated=True` models a hypothetical incumbent to
test suspension; it does not refer to actual officeholders. Model `ticks` are
abstract logical units; they are neither FRG heights nor seconds. Test amounts,
30-tick qualification, 2-reviewer quorum and other constants are arbitrary
fixtures, not adopted economics or operational thresholds. A model invocation
checks one snapshot; callers must not claim it monitors ongoing authority.

Run from repository root:

```sh
python -m unittest discover -s research/governance_bonds -p 'test_*.py'
python -m unittest discover -s services/governance_api -p 'test_*.py'
node --test services/governance_api/test_admin_ui.cjs services/governance_api/test_registration_ui.cjs
```

The governance regression suite requires its existing requirements file. The
research tests need only Python's standard library. Existing practice-election
records, routes and frozen snapshots are unchanged. Practice miner approvals
remain demo approvals and do not satisfy this proposed bond policy.

## Required gates before implementation with funds or authority

1. Ratify balanced representation, selection/removal, appeals, anti-Sybil and
   independent reviewer governance. Review collateral accessibility and pool
   concentration; do not equate wealth with independence.
2. Specify atomic minimum amount, qualification time basis, term/cooldown,
   confirmation depth, mining windows, freshness and reorg rules. The charter's
   provisional 30-day research target is not an activated rule.
3. Independently review and demonstrate native lock, mining attribution,
   ownership/amount/unspent/uniqueness proofs and privacy with adversarial tests.
4. Design atomic authorization checks, tamper-evident evidence history, reviewer
   revocation, replay protection and fail-closed monitoring; independently audit.
5. Obtain explicit approval for any native protocol/wallet changes in a separate
   proposal, with consensus compatibility and voluntary adoption assessment.
6. Review isolated end-to-end trials and recovery procedures before separately
   authorizing any funded bond program or binding election. Until then, stop at
   synthetic tests; no deposits, production credentials or binding votes.
