# Native FRG governance bond — implementation decision gates

**Status:** research only, October 22, 2026. No funded bonds, production API, voting authority, changes to native transactions or consensus.

This memo follows [the synthetic miner-bond policy](README.md). Its purpose is to prevent a synthetic eligibility result from being mistaken for a verifiable, privacy-preserving native FRG lock. **No bridge to Solana and no secondary token issuance** is involved.

## The essential test

A successful candidate must simultaneously establish:

1. A specified quantity of **native FRG** is controlled by the candidate or an independently authorized bond arrangement.
2. Its canonical on-chain evidence is unique, sufficiently confirmed and bound to the intended FRG network.
3. The locked amount cannot be spent before the specified representative-term end plus cooldown.
4. A publicly checkable or independently auditable proof establishes continuing unspent status despite native privacy mechanisms.
5. The proof cannot be reused across miners, elections, pools, or unrelated credentials.
6. The proof can be revoked after reorgs, lost verification, withdrawal, or conflicting evidence before the next authorized vote.
7. Withdrawal after the commitment is practical and safe without relying on the good will of an administrator.
8. Neither private keys nor unrelated wallet activity become public.

**Current result:** None of these is demonstrated end-to-end by PR #10; all are required before any funded trial.

## Candidate mechanisms to investigate

| Mechanism | Advantages | Blocking concern | Status |
| --- | --- | --- | --- |
| Native consensus-enforced time-locked output | Does not depend on a third-party custodian | Wallet construction and spend rules may reject or not securely support user-generated locks; private amount and unspent verification unresolved | Research only |
| Separate threshold-controlled native FRG escrow | Could enforce policy without a new consensus rule | Custodial/collusion risk, key recovery, reserve verification, withdrawals, and key image accounting | Not selected |
| Off-chain wallet signed pledge, frozen wallet balance, or screenshots | Easy demonstration | Does **not** enforce a lock; balance could be spent or reused | Rejected |
| Governance-specific native protocol modification | Could support an auditable primitive if independently proven | New consensus/security assumptions and network upgrade costs | Not authorized |

A minimum token balance without a provably enforceable lock is **not** a bond. Neither pool-issued work shares nor a single signature establishes miner identity.

## Isolation and review sequence

**Gate A — read-only source review.** Examine the actual FRG consensus transaction unlock rules, ordinary wallet construction restrictions, earliest possible spending, unlock-time leeway and any special-cased coinbase behavior. Cite exact source revisions. Do not patch wallet checks to manufacture a passing result.

**Gate B — disposable isolated native testnet.** Construct transactions using supported wallet operations only, fund with disposable testnet FRG, verify consensus acceptance and independent full-node agreement, then attempt premature spending at multiple heights and timestamps. Test earliest legal spend, reorg rollback, daemon restart and wallet recovery. Never use production keys or mainnet funds.

**Gate C — private proof research.** Evaluate how independent reviewers could verify amount, ownership, unspent state and unique bond commitment without exposing other outputs. Distinguish a proof that a deposit happened from proof the funds remain unspent. Evaluate key image / view-only limitations and whether any method breaks ring privacy or linkability. Failure here blocks deployment even if a lock transaction is accepted.

**Gate D — miner attribution research.** Verify actual accepted solo blocks and independently corroborated pool share data. Prevent one pool and its workers from claiming the same work twice. Disallow operator self-certification.

**Gate E — adversarial operations.** Include reorgs, monitoring outages, colluding reviewers, split identities, reused evidence, orphaned blocks, expired locks, withdrawn/compromised keys and deliberate refusal to return custodial funds. Require fail-closed authorization and independent appeal paths.

**Gate F — governance ratification.** Set bond minimum, term, 30-day qualification target, cooldown, seat balance, suspension timing, appeals and affordable access for small miners through a public, reviewed proposal. **No automatic increase in votes proportional to bonded amount or hash rate.** A strong bond cannot substitute for verified mining, and mining without a bond must remain permitted.

## Decision outcomes

- **All safety/privacy gates passed:** propose an independently audited, strictly limited development implementation and new opt-in tests; still no binding votes until separately authorized.
- **Enforceable lock exists but cannot be independently verified:** stop, keep miner governance eligibility provisional and nonbinding.
- **Only custodial escrow is feasible:** publish explicit trust, solvency, recovery and liability risks; seek a separate governance decision rather than silently treating custody as trustless bonding.
- **No defensible bond design:** do not activate governance bonds. Consider verifiable mining participation with independently reviewed *nonfinancial* eligibility controls as a separate constitutional alternative.

## Anti-shortcut rules

Do not call a Solana token stake a native FRG bond. Do not add a mint, stake APY, yield, slashing, fee diversion, permanent delegate or claim on future issuance. Do not wire `research/governance_bonds/model.py` into the admin API or practice-election authorization. Synthetic `candidate_for_review` never implies active credentials.
