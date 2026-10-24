# ForgeCoin Roadmap

> **Owner policy update (2026-10-24):** The public development chain and fresh candidate are separate, with no automatic balance migration. A retained genesis output must be independently proven permanently unspendable. Intended issuance is 100% PoW miner subsidy, no ICO/founder premine and a 0.20 FRG tail, subject to source audit. Candidate difficulty values remain provisional. A 10-seat native FRG chamber is only a design target; seats and founder rights are unratified.

> **Verified tests (2026-10-24):** Isolated Windows candidate accepted blocks through RPC height 17 including first post-LWMA block. Repeat offline heavier-chain reorg passed with restart and cleanup. 105 height-90/91/92 calculation cases matched on Windows x64 and Linux x86-64, not ARM64. Native block acceptance through those heights and genesis permanent unspendability remain unverified.

**Updated:** 2026-10-24
**Active scope:** Native ForgeCoin (FRG) only; no Solana token issuance.

## Pre-launch research — zero-dollar mining pool feasibility (not deployed)

- Investigate hosting a native FRG Stratum pool on existing Oracle Always Free ARM64 resources, subject to verified remaining quota, plus a home-desktop fallback.
- Compare a conventional pool with share accounting and operator-controlled payouts against a ForgeCoin-specific P2Pool fork with direct noncustodial payouts. Neither is proven compatible or public-ready.
- Require isolated multi-miner RandomX share tests, native block acceptance, mature payout reconciliation, reorganization and failure recovery, wallet custody audit and network hardening.
- Do not reconfigure the live Oracle development daemon, expose unrestricted RPC, or rely on paid services or trial credits.
- Owner-approved initial target: 1% operator fee, both solo and pool mining, a planned cap of 100 concurrent worker connections, and a caption disclosing that the project pool will initially be the only advertised pool until independent pools exist. Capacity must be enforced and load-tested before being marketed as operational. Architecture, payout rules, deployment isolation and launch dependency remain open.
- [Read the zero-cost mining pool research](docs/ZERO_COST_MINING_POOL_RESEARCH.md).

## Phase 1 — Independent native FRG network
- Validate native RandomX PoW mining, emission, peer discovery, wallet security, solo/pool payouts and chain reorganizations.
- Produce reproducible binaries, independent testnet coverage, public explorer and operational guidance.
- Preserve 100% of native FRG block subsidies for miners under native consensus.
- Do not introduce a Solana mint, wFRG dual-mining rewards, cross-chain token claims or Solana staking in V1.

## Phase 2 — Native FRG governance qualification
- Design **native FRG governance bonds** for miner representatives: independently verified mining activity plus continuously locked native FRG for a qualifying period.
- Specify and audit technically enforceable native-FRG lock proofs; a signed wallet balance alone does not establish an unspent, time-locked bond.
- Adopt explicit minimum amounts, lock duration, unbonding, ownership/uniqueness limits, reorg handling and loss-of-qualification rules **before binding authority**.
- Guarantee miners a meaningful designated constituency but no unilateral project-governance or native consensus override.
- Build representative accountability, protected votes, privacy-aware eligibility and independent audits. Existing election APIs and staking categories are practice-only.

## Phase 3 — Native adoption and trading
- Explore direct FRG exchange support and practical integrations without promising prices or listings.
- Support independent infrastructure and transparency. Do not use token issuance to finance these activities.

## Optional future research — Solana FRG market representation
**Deferred; not authorized for V1.**
Study a securely redeemable **1:1 FRG-backed Solana token** if direct native market access proves inadequate. This is *not* a second mining-issued currency. Require independently verifiable deposits and reserves despite native privacy, secure mint/burn/redemption, signer independence, legal/security review and demonstrated liquidity before deciding whether to launch. No mining-linked wFRG, Solana staking rewards, Token-2022 fees or activation blocks are committed.

## Historical designs
The earlier `ForgecoinDual-Mining-Tokenomics-Architecture.md` and v0.1 charter described speculative mining-linked wFRG issuance and staking. Those designs are **superseded**, not current instructions. Solana-focused prototype code may remain archived or labeled experimental, but must not be deployed or advertised as FRG V1 features.

## Development research artifact

See the [native FRG miner bond proposal and synthetic tests](research/governance_bonds/README.md). This isolated policy experiment verifies no real mining or lock proofs and grants no authority; production governance and native lock changes remain gated on independent review.
