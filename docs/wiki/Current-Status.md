# Current status and known limitations

**As of:** 2026-10-25, based on source inspection, GitHub issue/PR records and dated development test evidence. This is a status snapshot, not a live health monitor.

## Executive summary

ForgeCoin is a working **experimental codebase**, but **the new independent FRG mainnet and initial Windows desktop release are not approved for launch**. The public Oracle host serves an explorer connected to an **older development chain** and a separately marked static `/pool/` readiness page. The research listener performs **synthetic-only** RandomX checks; it does not accept public mining shares or issue rewards.

| Component / claim | Status | Evidence and limits |
| --- | --- | --- |
| Native ForgeCoin daemon, RandomX, wallets | Implemented / development chain active | Fork-specific consensus and wallet acceptance audit required; old chain must not be conflated with new candidate |
| Fresh-mainnet candidate | Tested in isolation, **not launched** | Candidate RPC template at height 1 was captured; prior isolated mining/fork-boundary evidence exists, not public launch approval |
| Windows Tauri wallet & local solo miner | Implemented; release **blocked** | Code supports wallet/node/miner controls; clean-package and genuine solo block acceptance/maturity remain mandatory |
| Custom pool mining in desktop via XMRig | Implemented UI/launcher; release **blocked** | Real trusted XMRig / FRG job acceptance, reconnect, telemetry and payout evidence missing |
| Web block explorer | Deployed for **old** chain | Oracle explorer/HTTPS observed; launch-network migration, independent verification and reorg-hardening remain |
| Static official-pool readiness page | Deployed | `/pool/` has no functional mining endpoint, payout backend or authenticated accounts |
| Pool Stratum-shaped research listener | Tested **synthetically only** | Loopback native RandomX, bounded sessions, failure/replay rejection; statuses explicitly uncredited |
| Durable pool accounting | Experimental models | SQLite synthetic journal fixes credited=0; offline ledger has no authoritative daemon/reorg/payout integration |
| Official public FRG mining pool | **Not launched** | 1% operator fee is proposed; no payouts, load certification or public production listener |
| Governance | Charter/prototypes | No binding on-chain FRG staking/voting enforcement or governance authority implementation proven |
| Solana wrapper, swaps, DeFi | Future research | No native FRG ↔ external asset settlement, bridge, wrapped supply or liquidity claimed |

## Validated evidence, not just planned features

- Isolated candidate-daemon `get_block_template` succeeded with a disposable wallet. Reported template: **height 1, difficulty 500,000, 76-byte hashing blob, 134-byte full template, reserved offset 124**. Earlier command shutdown returned exit 1; binary provenance and shutdown repeatability remain open. [Issue #28](https://github.com/tgibbsz32/forgecoin/issues/28).
- Template-header/nonce inspection observed a **4-byte little-endian nonce at dynamic offset 39** for the isolated test sample; this is not a full Stratum compatibility proof. [Issue #29](https://github.com/tgibbsz32/forgecoin/issues/29).
- An offline comparison reported **340/340 native `check_hash` versus Python threshold decisions**, using a development library rather than the fresh candidate. These are arithmetic checks, not live share acceptance. [Issue #29](https://github.com/tgibbsz32/forgecoin/issues/29).
- Oracle development RandomX synthetic tests, journal/crash refusal, bounded native-worker checks and loopback socket regression tests were reported passing in the [dated pool handoff](../HANDOFF_ORACLE_POOL_2026-10-25.md). No public listener or payouts were activated.
- On 2026-10-25, an isolated Windows checkout of current `main` passed **21 selected tests**. Overlaying proposed PR #27 hardening passed **23 selected tests** and **53 further research tests (three platform-specific skips)**. These sets overlap; they are **not** a claim of 97 independent checks. [PR #27](https://github.com/tgibbsz32/forgecoin/pull/27) is not merged.
- The downloaded XMRig Windows archive's SHA-256 does **not** match the publisher's named release-archive hash; no malware conclusion follows, but that binary is unapproved for packaging or execution. [Issue #95](https://github.com/tgibbsz32/forgecoin/issues/95).

## Open release-blocking issues

| Priority | Item | Why it matters |
| --- | --- | --- |
| High | [#95 — trusted XMRig provenance](https://github.com/tgibbsz32/forgecoin/issues/95) | Reproducible or publisher-verified miner required before executing/staging |
| High | [#29 — native job equivalence](https://github.com/tgibbsz32/forgecoin/issues/29) | Synthetic header/target calculations do not establish real candidate Stratum work |
| High | [#30 — native shares and safety](https://github.com/tgibbsz32/forgecoin/issues/30) | No production acceptance/crediting until real PoW, replay, target, staleness and resource tests pass |
| Medium | [#28 — template capture provenance](https://github.com/tgibbsz32/forgecoin/issues/28) | Exact candidate build identity, clean shutdown and reproducible isolation incomplete |
| High | Release checklist | Genesis spendability, cross-platform consensus, emission/fork tests, independent audit and verified desktop Solo+Pool tests |

## PRs needing disposition

Draft/review work includes [#4](https://github.com/tgibbsz32/forgecoin/pull/4) (proposed difficulty spec), [#26](https://github.com/tgibbsz32/forgecoin/pull/26) (daemon flags), [#27](https://github.com/tgibbsz32/forgecoin/pull/27) (loopback/proxy/redirect safety), [#31](https://github.com/tgibbsz32/forgecoin/pull/31) (offline job envelope), and Windows race/fault research [#54](https://github.com/tgibbsz32/forgecoin/pull/54) / [#60](https://github.com/tgibbsz32/forgecoin/pull/60). Check GitHub for live state before relying on this snapshot. PR #90 was closed unmerged because its PE-check regression was superseded by merged PR #91.

**Not verified:** public pool acceptance, actual pool payouts, completed desktop V1 release acceptance, independent security review, new-mainnet launch, user asset price or liquidity.
