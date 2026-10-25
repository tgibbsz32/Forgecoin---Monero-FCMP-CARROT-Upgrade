# ForgeCoin native atomic swaps + TSS-secured block-trading venue: SOLANA-FIRST

**Planning baseline:** 2026-10-25. **Research only.** No live funds, no contracts deployed, no real swaps, no FCMP++ port, no genuine threshold signatures, no user anonymity guarantees.

## Network selection — owner directive

**Solana replaces Ethereum as the execution/settlement chain.** Remove ERC-20, ETH gas/contract, Ethereum atomic-swap contract, Sepolia/EVM and Ethereum custody from the initial scope.

- **Private side:** independent ForgeCoin (FRG) Monero-derived FCMP++/CARROT **after** full native consensus integration.
- **Public side:** Solana mainnet in a future approved release; **local validator/devnet only for development**.
- **First payment assets:** native SOL (lamports) and **Solana USDC under the original SPL Token Program** (6-decimal token amounts; verify mint/network at runtime).
- **Owner's planned 55M standard SPL ecosystem token** (4M sale, 1M participation rewards, 50M future allocation) remains a *separate issuance/economics decision*. It is not a 1:1 backed FRG claim by default.
- Any FRG-backed wrapped claim must have equal, demonstrably spendable native FRG reserves. Neither it nor the proposed FCMP++-private stable asset exists in production.

## Two complementary products: different security models

**A. Peer-to-peer trust-minimized native swap.** An owner and counterparty lock native FRG under an FCMP++/CARROT-compatible scriptless, combined-spend-key construction, with a linked lock/claim/refund on Solana. A secret revealed during authorized Solana claim must enable the entitled party to spend the ForgeCoin-side output. Abort/refund must not let either side take both assets. **No delegated TSS custodian is required for this direct user-to-user path.**

**B. TSS/MPC-controlled confidential RFQ venue.** A separately modeled optional venue for legitimate private block orders. Threshold-controlled vaults on Solana may provide custody and payout policy, but are **not trustless**: signer collusion, liveness failure and key share theft remain risks. The matching engine, private relay, collateral and fees require independent verification; visibility of the public Solana settlement must be described accurately. No wash trades, synthetic fake fills or misrepresented volume.

## Solana-side escrow: design for native SOL and original-program SPL

1. **Initialize:** For each unique swap, bind swap ID, counterparty, asset kind, verified SPL mint (if applicable), integer atomic-unit amount, claim/refund point commitments and absolute ordered deadlines. Lock funds in a **Program Derived Address (PDA)**-controlled account. Do not rely on a hard-coded account name or off-chain provider permission.
2. **Lock SOL:** Deposit lamports to a properly owned and initialized program escrow account with rent/exemption accounting.
3. **Lock USDC SPL:** Use an escrow token account controlled by a PDA and the **original SPL Token Program** (`TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`). Verify token mint, owner, amount, token program and recipient associated token account derivation. Avoid accidentally targeting Token-2022.
4. **Set ready:** The maker signals that the corresponding private-chain lock is independently verified. The Solana program cannot automatically verify FCMP++ without a purpose-built light-client/proof mechanism, so readiness alone is a user/counterparty protocol step and not a trustless oracle.
5. **Claim or refund:** Validate authorization and cryptographic public-point proof, enforce non-overlapping deadlines, and authorize PDA-controlled release using CPI. Claims may deliberately reveal secrets on Solana; do not promise this data is private.
6. **Recovery:** Handle rejected transactions, RPC unavailable, Solana finality uncertainty, wrong-network wallets, token-account ownership, reorgs, duplicate attempts and deadline races. Reconcile native unlocking/maturity timing.
7. **Privacy:** Native FCMP++ obscures spent-output selection, not *Solana* accounts, public output amounts or counterparties. Need independent privacy mechanism for confidential order matching/settlement.

**Existing nonproduction reference:** [SutureCash/core](https://github.com/SutureCash/core) explores Solana↔Monero scriptless swaps using Solana Curve25519 operations; its README explicitly states **pre-launch, unaudited and no mainnet deployment**. The documented SOL path is not evidence that USDC SPL handling or ForgeCoin's FCMP++/CARROT format is compatible. The source is GPL-3.0-or-later; do not copy it without license review and attribution.

## Implemented (offline only)

- `solana_escrow_sim.py`: deterministic Solana **SOL/original-program SPL** escrow state transitions and two-timeout claim/refund checks. **No cryptographic verification; test booleans stand in for evidence.**
- `dark_pool_sim.py`: exact RFQ/quote-asset fee & conservation preview, duplicate/self-trade rejection, quorum roster *policy*. **No real TSS, settlement, privacy or signature checks**; production hooks deliberately fail closed.
- `tests/test_solana_escrow_sim.py` and `tests/test_dark_pool_sim.py`: Python offline tests; no wallet secrets or network use.

Run only offline:

```powershell
python -m unittest discover -s services/atomic_swap_research/tests -p 'test_*.py' -v
```

## Required implementation gates

| Gate | Prerequisite and acceptance test |
| --- | --- |
| G1 — FCMP++ | Native proof, CARROT, reorgs, tree database and wallet integration tested on disposable chain; stable-asset protocol remains separate |
| G2 — Solana program | Audited Rust/Anchor native SOL and SPL escrow PDAs, Curve25519 point validation, checked integer arithmetic and CPI security; local validator tests |
| G3 — Cross-chain protocol | Independently analyzed combined-key and reveal protocol against *actual* ForgeCoin FCMP++/CARROT, abort/refund and timeout asymmetry tests |
| G4 — Atomicity & finality | Both directions, all adversarial state races, failed providers, chain rollbacks, malicious counterparty, proof/reveal ordering |
| G5 — TSS venue | Reviewed distributed key generation, N-of-M signer policy enforcement, recoverability, independently verifiable orders, custody separation and settlement guarantees |
| G6 — Identity/privacy & compliance | Third-party linkage tests, genuine market executions only, AML/sanctions assessment, legal review of any synthetic stable asset and paid exchange activity |
| G7 — Launch authorization | External audit, governance/treasury rules, explicit permission before deploying a contract, minting, custody or trading |

**Hard stop:** neither Python simulator connects to an RPC endpoint or signs any actual transactions. It is **not** a Solana program and it is **not** a live atomic swap or dark pool.
