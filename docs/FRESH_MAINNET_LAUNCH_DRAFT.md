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
