# ForgeCoin Roadmap

**Updated:** 2026-10-22  
**Active scope:** Native ForgeCoin (FRG) only; no Solana token issuance.

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
