# ForgeCoin Roadmap

> **Owner policy update (2026-10-24):** Owner direction: publish a separate fresh mainnet without automatic balances migration only after genesis-output permanent-unspendability proof and independent launch review. The candidate 500,000 start, 400,000 floor and LWMA90 from height 16 remain provisional. A revised **10-seat native FRG governance chamber** is a design task, not a ratified chamber; allocation and founder roles are pending review. See docs/OWNER_POLICY_DECISIONS_2026-10-24.md.


> **Documentation status (2026-10-24):** Validation status: isolated fresh-candidate native RandomX mining passed through RPC height 17, and a full offline competing-chain reorganization repeat passed including persistence and cleanup. 105 calculation vectors at heights 90-92 matched Python on Windows and Linux x86-64, but native block acceptance at those heights and ARM64 agreement are untested. Genesis zero-spendable-premine is unverified. See docs/RELEASE_STATUS_2026-10-24.md.


**Updated:** 2026-10-24
**Active scope:** Native ForgeCoin (FRG) only; no Solana token issuance.

## Pre-launch research: zero-dollar mining pool feasibility (not deployed)

- Investigate hosting a native FRG Stratum pool on existing Oracle Always Free ARM64 resources, subject to verified remaining quota, plus a home-desktop fallback.
- Compare a conventional pool with share accounting and operator-controlled payouts against a ForgeCoin-specific P2Pool fork with direct noncustodial payouts. Neither is proven compatible or public-ready.
- Require isolated multi-miner RandomX share tests, actual native block acceptance, mature payout reconciliation, competing-chain reorganization and failure-recovery tests; inspect wallet custody and network security.
- Do not reconfigure the live Oracle development daemon or expose unrestricted RPC. Avoid paid services or time-limited trial credits.
- Owner input required: pool architecture, operator fee, payout scheme, infrastructure separation and launch dependency.
- Full research: [Zero-cost FRG mining pool feasibility](docs/ZERO_COST_MINING_POOL_RESEARCH.md).


## Phase 1 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Independent native FRG network
- Validate native RandomX PoW mining, emission, peer discovery, wallet security, solo/pool payouts and chain reorganizations.
- Produce reproducible binaries, independent testnet coverage, public explorer and operational guidance.
- Preserve 100% of native FRG block subsidies for miners under native consensus.
- Do not introduce a Solana mint, wFRG dual-mining rewards, cross-chain token claims or Solana staking in V1.

## Phase 2 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Native FRG governance qualification
- Design **native FRG governance bonds** for miner representatives: independently verified mining activity plus continuously locked native FRG for a qualifying period.
- Specify and audit technically enforceable native-FRG lock proofs; a signed wallet balance alone does not establish an unspent, time-locked bond.
- Adopt explicit minimum amounts, lock duration, unbonding, ownership/uniqueness limits, reorg handling and loss-of-qualification rules **before binding authority**.
- Guarantee miners a meaningful designated constituency but no unilateral project-governance or native consensus override.
- Build representative accountability, protected votes, privacy-aware eligibility and independent audits. Existing election APIs and staking categories are practice-only.

## Phase 3 ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Native adoption and trading
- Explore direct FRG exchange support and practical integrations without promising prices or listings.
- Support independent infrastructure and transparency. Do not use token issuance to finance these activities.

## Optional future research ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Â Solana FRG market representation
**Deferred; not authorized for V1.**
Study a securely redeemable **1:1 FRG-backed Solana token** if direct native market access proves inadequate. This is *not* a second mining-issued currency. Require independently verifiable deposits and reserves despite native privacy, secure mint/burn/redemption, signer independence, legal/security review and demonstrated liquidity before deciding whether to launch. No mining-linked wFRG, Solana staking rewards, Token-2022 fees or activation blocks are committed.

## Historical designs
The earlier `ForgecoinDual-Mining-Tokenomics-Architecture.md` and v0.1 charter described speculative mining-linked wFRG issuance and staking. Those designs are **superseded**, not current instructions. Solana-focused prototype code may remain archived or labeled experimental, but must not be deployed or advertised as FRG V1 features.

## Development research artifact

See the [native FRG miner bond proposal and synthetic tests](research/governance_bonds/README.md). This isolated policy experiment verifies no real mining or lock proofs and grants no authority; production governance and native lock changes remain gated on independent review.
