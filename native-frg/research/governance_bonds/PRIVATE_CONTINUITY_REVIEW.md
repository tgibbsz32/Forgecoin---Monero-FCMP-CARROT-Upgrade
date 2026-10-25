# Native FRG bond privacy and continuity review

Research only. Source baseline: `6f215b38bc2d07a5bb572c6592936ccb07cb4481`
(merged PR #13). No native code, governance service, funds, or binding policy
is changed. The earlier disposable regtest established mature wallet funds;
it did not establish a nonzero-unlock bond. No new native experiment was run
for this review.

## Finding

The existing reserve proof is a useful **selective-disclosure primitive**, but
is not a privacy-preserving continuous governance bond as currently implemented.
It can expose selected holdings and their spend linkage to a recipient. It does
not enforce a lock, bind its daemon reads to one agreed checkpoint, or establish
continuous mining qualification. This is a finding about the existing interface,
not a claim that a future cryptographic construction is impossible.

There are two independent blockers: a supported enforceable bond construction,
and a reviewed proof/continuity protocol with explicit privacy guarantees.
Solving one does not solve the other.

## Source evidence

Links pin the reviewed revision, so later source movement cannot silently
change the basis of these observations.

| Source | Observed behavior | Consequence for a proposed bond |
| --- | --- | --- |
| [wallet2.cpp, get_reserve_proof](https://github.com/tgibbsz32/forgecoin/blob/6f215b38bc2d07a5bb572c6592936ccb07cb4481/src/wallet/wallet2.cpp#L13230) | Selects unspent, nonfrozen transfers; serializes transaction ID, output index, key image, shared secret and signatures. Optional minimum-reserve selection chooses whole outputs. | A minimum amount request is not a zero-knowledge threshold proof; selected outputs can exceed the requested amount. A wallet freeze is local and excluded by this selection path. |
| [wallet2.h, reserve_proof_entry](https://github.com/tgibbsz32/forgecoin/blob/6f215b38bc2d07a5bb572c6592936ccb07cb4481/src/wallet/wallet2.h#L795) | Encodes output references, key image and shared-secret material. | Base58 encoding is not encryption. Sharing a proof shares this material. |
| [wallet2.cpp, check_reserve_proof](https://github.com/tgibbsz32/forgecoin/blob/6f215b38bc2d07a5bb572c6592936ccb07cb4481/src/wallet/wallet2.cpp#L13350) | Checks duplicate outputs/key images within a proof; verifies output/key-image and address relationships; decodes RingCT amounts; returns total and spent amounts. | The verifier learns selected amounts and the specific output/key-image linkage. In-proof duplicate rejection is not a registry preventing reuse across different claims. |
| Same checker | Fetches transactions and key-image spent status in separate daemon RPCs; rejects transactions marked in-pool. There is no agreed checkpoint hash or required confirmation-depth input. | A valid signature is not independent validation of the daemon's chain view. Separate reads can straddle tip changes/reorgs. No lock-horizon check is performed. |
| [tx_pool.cpp](https://github.com/tgibbsz32/forgecoin/blob/6f215b38bc2d07a5bb572c6592936ccb07cb4481/src/cryptonote_core/tx_pool.cpp#L194) | Rejects nonzero transaction unlock time when `!kept_by_block`. | Removing wallet guards alone would not establish ordinary relay acceptance. The exception is not evidence of supported bond creation or complete block acceptance. |
| [blockchain.cpp, is_tx_spendtime_unlocked](https://github.com/tgibbsz32/forgecoin/blob/6f215b38bc2d07a5bb572c6592936ccb07cb4481/src/cryptonote_core/blockchain.cpp#L3848) | Height check is `db_height - 1 + delta >= unlock_time`; timestamp check uses fork-dependent time/leeway. | Lock coverage must use the earliest consensus spend boundary, not a wallet display or expected block duration. |

The reserve-proof challenge hashes the supplied message, address and key images.
A future application could bind a canonical, domain-separated context through
that message; the existing checker does not interpret a network, policy, term,
entity or challenge schema. A message signature alone does not authenticate the
chain checkpoint or establish global uniqueness.

For a height lock U and allowed delta D, the displayed source predicate becomes
true at database height H satisfying H >= U + 1 - D (assuming nonempty chain
and ordinary arithmetic bounds). H counts blocks; it is not the tip index.
With D=1 it becomes H >= U. This algebra describes that predicate only, not a
complete native spend test: maturity, inputs, transaction validity and the
calling validation context still matter. A height horizon cannot promise a
fixed number of days. Timestamp wallet leeway also uses different selection
logic from the daemon; [the earlier review](SOURCE_UNLOCK_REVIEW.md) remains
an open native-test gate.

## Privacy choices that remain unresolved

Publishing reserve proofs would let anyone receiving them link selected outputs
to their key images, recognize their later spends, and decode selected amounts.
Giving proofs only to reviewers narrows the audience but introduces disclosure
and retention trust; it is not equivalent to publicly verifiable zero knowledge.
The daemon also receives queried transaction IDs and key images. A dedicated
wallet may reduce unrelated disclosure but does not remove these linkages.
No real proof, address, key, or transaction is included in this research.

A future private construction would need a reviewed relation proving canonical
inclusion, control, amount threshold and enforced horizon, plus non-spend and
duplicate-use prevention. The amount commitment must be tied to the same actual
output as the control/lock proof. A nullifier would need a defined scope that
detects prohibited reuse across overlapping terms without unnecessarily linking
unrelated activity. A claimant-chosen commitment or hash cannot establish that
relation. No scheme, implementation, security proof or performance claim is
selected here. Independent cryptographic review is required.

## What continuity actually requires

Distinguish historical qualification from future nonspendability. Even perfect
past coverage cannot create a future lock. For one immutable, canonically
included output with a proven enforced horizon, validated chain history can in
principle support historical non-spendability without polling every block. That
still requires the output's canonical ancestry, confirmation rules, actual lock
semantics and private proof relation. It does not establish ongoing mining,
reviewer independence, absence of withdrawal, or unique governance use.

A series of balance snapshots can switch outputs and conceal qualification
gaps. It cannot be relabeled as interval evidence. Replacing a bond, changing a
credential/term, or invalidating chain history requires revalidation; qualifying
time must not silently carry across an unproven interval. An outage is unknown
coverage unless independently reconstructed history proves the required facts.
During uncertainty the earlier proposal suspends hypothetical authority.

`continuity.py` is a separate, pure interval-coverage experiment. Its invented
windows assert **all** qualification predicates over `[start, end)` in abstract
ticks. It tests union coverage for the same network, policy, entity, bond, term
and history revision. A history revision labels one agreed canonical history,
not every advancing chain tip; it cannot verify ancestry. Mixed contexts fail
closed even if another window covers the query. Every result has
`binding_authority == False`. There is no monitoring or authorization integration.

The adversarial tests cover gaps, recent-only observations, duplicate/overlapping
windows, out-of-order intervals, replacement/replay, and reorg invalidation.
Passing these tests demonstrates interval logic only. Inputs remain fabricated
assertions, not signatures, native evidence, independent reviews or proof of
lock enforcement. Future native tests must separately establish relay/block
acceptance, early-spend rejection, recovery and two-node chain agreement; future
proof tests must include replay, malformed proofs, dishonest daemon responses,
cross-checkpoint reads, reused outputs and privacy leakage assessment.

Run the existing research discovery command to include these scenarios:

```sh
python -m unittest discover -s research/governance_bonds -p 'test_*.py'
```

Decision: retain research-only status. No deposit API, funded lock, new consensus
rule, or binding governance is justified by these results.
