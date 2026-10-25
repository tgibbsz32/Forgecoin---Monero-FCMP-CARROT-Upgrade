# ForgeCoin FCMP++ privacy network and cross-chain trading: design baseline

**Status:** proposed engineering direction, 2026-10-25; **NOT implemented, audited, deployed, or approved for a mainnet fork or public trading.**

## 1. Goal and claims

ForgeCoin (FRG) is intended to remain an independent Monero-derived, RandomX proof-of-work L1 with native confidential transfers. The new development target is to adopt **FCMP++ full-chain membership proofs** with the compatible **CARROT wallet/address system**, then build **native FRG ↔ Solana** swap capabilities, beginning with original-program SPL **USDC** and native **SOL**, plus a separately governed privately matched block-trading facility. Ethereum/ERC-20 is not in this implementation plan.

Required public language: FCMP++ hides which **eligible historical output** is spent within a much larger set; it does **not** assert the chain publicly knows which outputs remain unspent, guarantee absolute anonymity, or automatically hide metadata exposed by relayers, exchange accounts, RPC infrastructure, counterparties or transparent chains.

**No presale, synthetic stablecoin, deployed custody, bridge-issued collateral, mint or governance authority is created by this design document.**

## 2. Verifiable upstream baseline and network separation

- FCMP++/CARROT beta stressnet v3.0 activated a test fork on October 5, 2026 at **test-network height 3,102,800**, not Monero mainnet. The v3.1 pinned source was inspected at commit `d80596ad18110390b6ca97a77e29aba36f4644c9`.
- Upstream beta source: https://github.com/seraphis-migration/monero/releases/tag/v0.19.0.0-beta.3.1
- October 2026 Monero consensus review: https://github.com/monero-project/monero/pull/11440 and https://github.com/monero-project/meta/issues/1470
- ForgeCoin source-presence survey and blockers: draft PR https://github.com/tgibbsz32/forgecoin/pull/100 . Source-presence checks do NOT constitute a successful FCMP++ port.
- FCMP++ beta hardfork numbering must not be copied into the ForgeCoin candidate: the isolated ForgeCoin chain has already proposed v19 rules at height 1, a distinct genesis, separate address prefixes and port numbers, and independent difficulty logic.
- The existing ForgeCoin development chain and the proposed fresh mainnet are separate: **no automatic migration of balances or coin claims**. The unresolved candidate genesis output and its permanent unspendability remain an independent launch gate.

## 3. FCMP++ core consensus integration (release-blocking)

| Area | Planned implementation | Required evidence |
| --- | --- | --- |
| Cryptographic verifier | Pin and port Rust FCMP++ proof implementation, FFI/C++ bindings, generalized Bulletproof/curve-tree membership verification and spend authorization/linkability | Independent input vectors, invalid-proof rejection, exact pinned dependency provenance, overflow/DoS tests |
| Global curve tree | Persist deterministic output commitments, tree-layer/root state, reference-block semantics, incremental updates | Full sync, restart, rollback, pruning and alternative-branch agreement on Windows/Linux x86-64/ARM64 |
| Blockchain database | Update LMDB schema and migration/rebuild logic for output accumulator and reorg-safe indexes | Backup/restore, crash/recovery tests, storage/memory/CPU benchmarks and historical-state agreement |
| Transaction format | Adopt vetted FCMP++ serialization, output formats, block commitments and version-gated rejection rules | Golden vectors, canonical encoding, malformed input tests and cross-node acceptance |
| Historical verification | Retain verification for legacy historical signatures at their valid heights | Old-chain sync and historical transaction validation; new-format rules only at approved activation |
| CARROT wallet integration | Port carrot_core/carrot_impl, scanning and keys; plan legacy-output spending/restore, watch-only/offline signer compatibility | Wallet restore, recovery, view-only, address migration and old-output spend tests |
| Tx-pool/hardfork | Revalidate whole mempool across hardfork boundary; enforce version-specific proof/fee/weight and duplicate-spend rules | No stale-invalid transactions survive transition, honest transactions survive, bounded memory/CPU under adversarial input |
| Crypto performance | Benchmark upstream-supported optimizations; investigate `fe_pow22523` factoring only if required by verified upstream change | Same outputs as reference, fuzz tests, no algorithm change hidden as optimization |
| Fork-specific economics | Preserve 50M FRG primary reference (not a cap), perpetual 0.20 FRG tail, 100% PoW miner subsidy, approved difficulty parameters and zero *allocated* premine direction | Reproducible native consensus tests and genesis spendability proof; never replace source constants blindly |

**Important:** TSS/MPC bridge plans must not be merged into native block validity or used to bypass FCMP++ release evidence. A hardfork must require explicit authorization and community upgrade procedure.

## 4. Native ForgeCoin ↔ Solana atomic swaps and optional private block-trading venue

**Execution-chain decision:** Solana replaces Ethereum/EVM. All new direct-swap contracts must be **Solana programs** (PDA-controlled lamports/SPL token accounts, Curve25519 compatibility reviewed for CARROT). SOL and **Solana USDC (original SPL Token Program)** are the initial settlement assets; confirm mint and decimal precision on the selected network. No Ethereum/ERC-20 implementation is authorized by this research plan.

**Trust-model separation:** A real user-to-user scriptless atomic swap should not require a TSS custodian; a separate TSS/MPC-secured order venue introduces signer-quorum custody risk and is **not fully trustless**. Native FRG scriptless claims require a proven FCMP++/CARROT-compatible shared-key construction, an audited Solana claim/refund escrow program, cryptographically checked revealed scalar/public point relation, and adversarial two-timelock safety tests. SOL and SPL have distinct custody/transfer paths; neither is deployed. Offline state-machine tests are **not** atomic swaps.

**Research reference:** [SutureCash/core](https://github.com/SutureCash/core) prototypes unaudited pre-launch Monero↔Solana swaps; its SOL implementation and GPL-3.0-or-later source do **not** prove original SPL USDC or ForgeCoin FCMP++/CARROT compatibility.

### 4.1 The separate confidential-trading venue

**Goal:** enable legitimately authorized parties to express sizeable orders without broadcasting their intent in advance, while preserving accurate financial ledgers, fair settlement and applicable financial compliance.

### 4.1 Components

1. **Native FRG escrow or verified reserve custody:** detect incoming confidential FRG using isolated wallet/RPC tooling, require source-network confirmations, and record liabilities without publishing customers' native wallet histories. A private view key alone is NOT proof of unspent reserves.
2. **Threshold-controlled vaults:** investigate TSS/MPC on Solana-native SOL and verified original-program SPL tokens with independent signers, key rotation, quorum, pause/recovery, and public proof of authority constraints. Threshold signatures reduce a single-key failure but are **not automatically trustless** or decentralized.
3. **Authenticated relayer transport:** private order submission to reduce information exposure; blind credentials or zero-knowledge claims may be investigated to decouple public identifiers. Relayers must not be trusted to mint or double-execute without verification.
4. **Private matching:** confidential/RFQ or batch auction design with independently verifiable order ownership and price/quantity conservation, counterparties' fairness and transparent execution terms. Avoid advertising a public DEX fill as hidden if its final trade is visible.
5. **Settlement and withdrawal:** both assets must change ownership under enforceable atomic/escrow conditions; cross-chain settlement cannot be called instant solely because Solana's on-chain leg is fast. Native FRG confirmations and release risk remain.
6. **Observability and safeguards:** separate genuine execution ledger from optional harmless encrypted cover packets. Do not post wash trades, fake liquidity/volume, or counterfeit fills.

### 4.2 Supported pairs and liquidity

- Research Solana-native SOL and **Solana USDC** first using funded test balances and explicit liquidity quotes. Expand only to reviewed Solana SPL assets after verifying each mint, token-program ownership, decimal precision, transfer restrictions, liquidity and escrow compatibility.
- A 1:1 redeemable `wFRG` token requires **1:1 verifiable native FRG backing** and burned/escrowed supply on redemption. A future `wFRG` bridge mint must not assume that the unrelated 55M SPL allocation is collateral.
- **55M standard SPL-token planning allocation:** 4M sale, 1M participation rewards, 50M reserved future issuance/utility. This is a separately governed economic design unless and until the issuer specifies legally and technically enforceable FRG redemption rights. Neither project is deployed to Solana mainnet.
- Pool **1% optional service fee**, native **FRG treasury receipts**, prospective SPL sale proceeds, bridge reserves and bridge routing fees are separate books. A basis-point **bridge fee remains unspecified** until independently approved, disclosed and assessed.
- Any US-dollar-linked *synthetic stable asset* is **future feasibility research only**. Peg design, reserves/redemption, lawful issuer status, insolvency management and price feed risk must be designed and reviewed before it can be represented as stable.

### 4.3 Claims and constraints

- **Confidential source funds** does not imply invisible Solana settlement: public SPL ownership, token account changes, trade size, routing or counterparty activity can leak data.
- Solana has no globally shared public mempool, but information exposure to leaders/builders and post-settlement MEV exists. Use realistic privacy and price-execution threat models.
- TSS/MPC custody is one potential trust model, not a cryptographic proof of reserve or safety. Cross-chain 'trustless atomic swap' requires a specific formally analyzed protocol and refunds/timeouts, not simply adding a vault.
- Privacy functions must coexist with legitimate lawful-order processing, sanctions controls and applicable customer-identification/AML obligations. The protocol is **not designed as an offshore evasion or sanctions-bypass service**.
- The 2025 GENIUS Act imposes requirements on covered payment stablecoin issuers; no legal exemption or risk-free synthetic issuance is inferred from use of a private L1. Seek qualified financial regulatory review **before** a sale, paid custody, stablecoin or exchange service.

## 5. Program phases and hold points

| Phase | Planned output | Go/no-go rule |
| --- | --- | --- |
| P0 — Source + protocol review | Full upstream FCMP++ beta v3.1 source integration matrix and version mapping | No patch to live consensus; explicit reproducible reference and unresolved genesis handling |
| P1 — Native FCMP++ integration | C++/Rust/CARROT and DB in isolated candidate, format/consensus tests | Proof/mempool/chain validity must pass without inflation, reorg or historical-sync failures |
| P2 — Cross-platform stress | Two-node/three-platform sync, wallets, mining, full reorg/pruning and resource benchmark | Independent code and cryptographic review; explicit mainnet fork and launch authorization |
| P3 — Solana-side offline prototype | Native SOL/original-program SPL swap state model, claim/refund timings, private RFQ simulation, fee accounting, TSS threat model | No Solana program deployed, real TSS signatures, collateral, token issuance, paid orders or funds moved |
| P4 — Solana localnet/devnet proof | Real program-owned SOL/SPL escrow, verified scalar/public-point checks, cross-chain FRG/CARROT claim/refund and separately tested threshold vault/private RFQ | Independently test atomicity, timeout/failure recovery, linkage/privacy, custody/issuer/regulatory review before any deployment decision |

## 6. Security invariants / tests

- Invalid membership proof, forged tree root, malformed serialization, excessive proof size, duplicate nullifier or fake output issuance must be rejected, including across reorgs and restarts.
- Test time-lock/coinbase maturity, reward issuance and timestamp/difficulty changes **alongside** FCMP++ activation.
- Historic ring verifier and old wallet scanner must remain valid for historic transactions. CARROT must not silently convert other people's old-chain balances.
- Bridge assets: **actual spendable reserves >= redeemable liabilities**, no delayed/duplicate payouts, no replay, no uncredited or false trades, sufficient recovery under signer failure or chain reorg.
- Model threats from public observers, bridge signers, relayers, MEV bots, validators, market counterparties, and seized/compromised infrastructure. Publish observed anonymity limits and execution speed rather than promising perfect confidentiality or instant native finality.
- Governance remains unratified; no FCMP++, vault or issuance authority arises from an experimental vote or an unreleased 55M token.

## 7. Authoritative references and status

- [ForgeCoin FCMP++ audit / draft PR #100](https://github.com/tgibbsz32/forgecoin/pull/100)
- [Monero FCMP++ upstream beta v3.1 source](https://github.com/seraphis-migration/monero/releases/tag/v0.19.0.0-beta.3.1)
- [Monero FCMP++ consensus PR](https://github.com/monero-project/monero/pull/11440)
- [Monero Research Lab Oct 7 notes](https://github.com/monero-project/meta/issues/1470)
- [Solana MEV documentation](https://solana.com/docs/defi/mev-protection)
- [12 U.S.C. 5903](https://uscode.house.gov/us/usc/119-118/t12/s5903/)
- [ForgeCoin owner's native policy](https://github.com/tgibbsz32/forgecoin/blob/main/docs/OWNER_POLICY_DECISIONS_2026-10-24.md)

**Hard stop:** This plan is not permission to activate a fork, expose exchange endpoints, mint assets, take deposits, trade, transfer treasury funds, evade financial controls, or announce completion.
