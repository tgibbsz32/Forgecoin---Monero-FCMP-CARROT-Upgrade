# Fresh-mainnet launch: difficulty specification (draft)

> **Planning document, not an activation announcement.** The existing ForgeCoin development chain is unchanged. No chain reset, genesis replacement, or new-mainnet deployment is authorized by this document.

## Intended consensus parameters

| Parameter | Fresh-mainnet target |
| --- | --- |
| Initial mining difficulty | **500,000** |
| Minimum difficulty floor | **400,000** |
| Target block interval | **120 seconds** |
| Proof of work | RandomX (current ForgeCoin implementation) |
| Difficulty adjustment | ForgeCoin's integer LWMA variant after sufficient history |
| LWMA historical window | 90 solve intervals (91 samples) |
| Public launch status | Not launched |

The floor is a **minimum permitted difficulty**, not a maximum. Difficulty may rise above the 500,000 starting value as network hash power increases. The floor must apply to all consensus validation paths once enabled.

## Open consensus design: first blocks

The current ForgeCoin LWMA routine requires **91 timestamps/cumulative-work samples**. A new chain does not have that history at genesis. Before implementation, specify deterministic behavior for every height from genesis through the first LWMA calculation. One candidate is fixed 500,000 difficulty for the warm-up period followed by LWMA, with the 400,000 floor, but **that warm-up schedule has not been finalized or tested**. Confirm the exact first eligible height against block-height and sample-index semantics.

## Do not copy the development-chain schedule

The local development branch currently defines these distinct rules:

- At height 500: 500,000 difficulty floor (v17).
- At height 600: 1,000,000 difficulty floor (v18).
- At height 700: 90-interval LWMA (v19).

These **are not** the proposed fresh-mainnet activation parameters. The fresh-network configuration must explicitly replace the old schedule, not silently inherit its 1,000,000 floor.

## Required validation before launch

1. Implement a network-specific genesis, network identity, activation table, and difficulty parameters; prevent accidental peering with the old chain.
2. Test startup heights, LWMA activation, floor enforcement, exact 120-second target behavior, malicious timestamps, reorganizations, and alternate-chain verification.
3. Confirm deterministic consensus results across supported Windows x64 and Linux ARM64 builds.
4. Audit existing development-chain mining, any distributed balances, independent users, and checkpoint obligations. Do not reset or invalidate balances without an explicit public transition decision.
5. Produce verified reproducible release candidates and publish their hashes, limitations, and clear migration instructions.
6. Announce a fair public start time and give independent miners and node operators adequate notice.

## Transparency and network status

ForgeCoin remains an **experimental development network** at the time of this draft, without an independent security audit. No public-mainnet reset or migration has been performed. The current explorer is [available over HTTPS](https://150.136.209.227/), but reflects the **existing development chain**, not a new launch.

The proposed economics and difficulty settings do not guarantee security, stable mining profitability, or fair distribution; these require testing and transparent public participation.


## Preliminary launch simulations — October 20, 2026

A **Python reproduction of the current integer LWMA formula**, parameterized for 60, 90, or 120 intervals and a 400,000 floor, ran 624 seeded trials (13 scenarios × 3 windows × 16 random seeds) across **386,880 simulated blocks**. Each trial simulated 620 blocks with a possible hash-rate transition after 220 blocks. Startup used a provisional **fixed difficulty of 500,000 until N+1 history entries**, before LWMA. This is **not approved consensus bootstrap logic**.

| Scenario, first 100 blocks after transition (seconds) | LWMA 60 | LWMA 90 | LWMA 120 |
| --- | ---: | ---: | ---: |
| One 6,500 H/s miner, steady | 119.52 | 118.58 | 117.38 |
| Large miner joins, 6,500 → 33,500 H/s | 78.71 | 63.77 | 53.22 |
| Large miner leaves, 33,500 → 6,500 H/s | 218.34 | 250.67 | 262.30 |
| Pool exit removes 70%, 65,000 → 19,500 H/s | 179.97 | 198.35 | 201.65 |
| Network at 2,000 H/s, last 200 blocks | 200.08 | 200.05 | 200.05 |

The 400,000 floor imposes a minimum expected block interval of 200 seconds at 2,000 H/s (difficulty / hash rate), irrespective of window. LWMA 60 reacts faster to large departures; 120 is slower; **90 remains a practical compromise, not a proven optimum**. Results are means over seeded trials, not deterministic guarantees, and rare long block gaps occur.

**Validation limits:** Python models the integer formula but does not link or execute the compiled ForgeCoin consensus implementation; it does not validate RandomX proofs, alternate chains, adversarial timestamps, propagation, or real pool payout behavior. The short warm-up period and sample indexing remain consensus design issues. Reproduce using the locally saved `simulate_fresh_mainnet.py` and CSV/JSON results in the project's `final-respository-and-builds/consensus-specs` folder. Do **not** treat these results as release authorization.

## Future development: optional XMR/XTM merged-mining integration

After ForgeCoin's own mainnet launch and stabilization, research an optional **Monero (XMR) + Tari (XTM)** merged-mining setup within ForgeCoin Desktop, including compatible external mining infrastructure, separate wallet support, secure key isolation, and pool integration. This roadmap item is *not* a plan to make ForgeCoin itself an auxiliary-POW chain, and it does **not** change ForgeCoin's existing consensus, block rewards, or launch scope.
